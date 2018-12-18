import logging

import simplejson
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.db.models import Sum, F

from coin_exchange.constants import ORDER_STATUS, CRYPTO_FUND_TYPE, CRYPTO_FUND_ACTION_STATUS, CRYPTO_FUND_ACTION
from coin_exchange.models import CryptoFund, Order, CryptoFundAction
from common.constants import DIRECTION, EXCHANGE_SITE, CURRENCY
from integration import coinbase, binance


class FundManagement(object):
    @staticmethod
    def update_in_fund(currency: str):
        fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.in_fund)
        sum_amount = Order.objects.filter(direction=DIRECTION.sell,
                                          status=ORDER_STATUS.success,
                                          updated_at__gte=fund.updated_at).aggregate(Sum('amount'))
        if sum_amount['amount__sum']:
            fund.amount = F('amount') + sum_amount['amount__sum']
            fund.save()

    @staticmethod
    def update_out_fund(currency: str):
        fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.out_fund)
        sum_amount = Order.objects.filter(direction=DIRECTION.buy,
                                          status=ORDER_STATUS.success,
                                          updated_at__gte=fund.updated_at).aggregate(Sum('amount'))
        if sum_amount['amount__sum']:
            fund.amount = F('amount') - sum_amount['amount__sum']
            fund.save()

    @staticmethod
    @transaction.atomic
    def transfer_in_fund_to_storage(currency: str, amount: Decimal):
        provider_data = {}
        if not settings.TEST:
            provider_data = FundManagement.crypto_transfer_in_fund_to_storage(currency, amount)

        in_fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.in_fund)
        in_fund.amount = F('amount') - amount
        in_fund.save()
        storage_fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.storage_fund)
        storage_fund.amount = F('amount') + amount
        storage_fund.save()

        action = CryptoFundAction.objects.create(
            from_amount=amount,
            from_currency=in_fund.currency,
            amount=amount,
            currency=storage_fund.currency,
            from_fund_type=CRYPTO_FUND_TYPE.in_fund,
            fund_type=CRYPTO_FUND_TYPE.storage_fund,
            action=CRYPTO_FUND_ACTION.transfer,
            status=CRYPTO_FUND_ACTION_STATUS.transferring,
            provider_data=simplejson.dumps(provider_data),
        )

        return action

    @staticmethod
    @transaction.atomic
    def transfer_storage_to_out_fund(currency: str, amount: Decimal):
        provider_data = {}
        if not settings.TEST:
            provider_data = FundManagement.crypto_transfer_storage_to_out_fund(currency, amount)

        out_fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.out_fund)
        out_fund.amount = F('amount') + amount
        out_fund.save()
        storage_fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.storage_fund)
        storage_fund.amount = F('amount') - amount
        storage_fund.save()

        action = CryptoFundAction.objects.create(
            from_amount=amount,
            from_currency=out_fund.currency,
            amount=amount,
            currency=storage_fund.currency,
            from_fund_type=CRYPTO_FUND_TYPE.storage_fund,
            fund_type=CRYPTO_FUND_TYPE.out_fund,
            action=CRYPTO_FUND_ACTION.transfer,
            status=CRYPTO_FUND_ACTION_STATUS.transferring,
            provider_data=simplejson.dumps(provider_data),
        )

        return action

    @staticmethod
    @transaction.atomic
    def transfer_in_fund_to_out_fund(currency: str, amount: Decimal):
        provider_data = {}
        if not settings.TEST:
            provider_data = FundManagement.crypto_transfer_in_fund_to_out_fund(currency, amount)

        in_fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.in_fund)
        in_fund.amount = F('amount') - amount
        in_fund.save()
        out_fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.out_fund)
        out_fund.amount = F('amount') + amount
        out_fund.save()

        action = CryptoFundAction.objects.create(
            from_amount=amount,
            from_currency=in_fund.currency,
            amount=amount,
            currency=out_fund.currency,
            from_fund_type=CRYPTO_FUND_TYPE.in_fund,
            fund_type=CRYPTO_FUND_TYPE.out_fund,
            action=CRYPTO_FUND_ACTION.transfer,
            status=CRYPTO_FUND_ACTION_STATUS.transferring,
            provider_data=simplejson.dumps(provider_data),
        )

        return action

    @staticmethod
    @transaction.atomic
    def convert_storage_to_vault(currency: str, amount: Decimal):
        provider_data = {}
        if not settings.TEST:
            provider_data = binance.send_sell_order('{}USDT'.format(currency), amount)
        storage_fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.storage_fund)
        storage_fund.amount = F('amount') - amount
        storage_fund.save()
        vault_fund = CryptoFund.objects.get(currency=CURRENCY.USDT, fund_type=CRYPTO_FUND_TYPE.storage_fund)
        vault_fund.amount = F('amount') + amount * Decimal(str(provider_data.get('price', 0)))
        vault_fund.save()

        action = CryptoFundAction.objects.create(
            from_amount=amount,
            from_currency=storage_fund.currency,
            amount=amount * Decimal(str(provider_data.get('price', 0))),
            currency=vault_fund.currency,
            from_fund_type=CRYPTO_FUND_TYPE.storage_fund,
            fund_type=CRYPTO_FUND_TYPE.storage_fund,
            action=CRYPTO_FUND_ACTION.convert,
            status=CRYPTO_FUND_ACTION_STATUS.converted,
            provider_data=simplejson.dumps(provider_data),
        )

        return action

    @staticmethod
    @transaction.atomic
    def convert_vault_to_storage(currency: str, amount: Decimal):
        provider_data = {}
        if not settings.TEST:
            provider_data = binance.send_buy_order('{}USDT'.format(currency), amount)
        vault_fund = CryptoFund.objects.get(currency=CURRENCY.USDT, fund_type=CRYPTO_FUND_TYPE.storage_fund)
        vault_fund.amount = F('amount') - amount
        vault_fund.save()
        storage_fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.storage_fund)
        storage_fund.amount = F('amount') + Decimal(str(provider_data.get('executedQty', 0)))
        storage_fund.save()

        action = CryptoFundAction.objects.create(
            from_amount=amount,
            from_currency=vault_fund.currency,
            amount=Decimal(str(provider_data.get('executedQty', 0))),
            currency=storage_fund.currency,
            from_fund_type=CRYPTO_FUND_TYPE.storage_fund,
            fund_type=CRYPTO_FUND_TYPE.storage_fund,
            action=CRYPTO_FUND_ACTION.convert,
            status=CRYPTO_FUND_ACTION_STATUS.converted,
            provider_data=simplejson.dumps(provider_data),
        )

        return action

    @staticmethod
    def crypto_transfer_in_fund_to_storage(currency: str, amount: Decimal):
        # from coinbase to binance
        address = settings.BINANCE['ACCOUNTS'][currency]
        resp = coinbase.send_transaction(address, currency, amount)
        return {'id': resp.id, 'src': EXCHANGE_SITE.coinbase}

    @staticmethod
    def crypto_transfer_storage_to_out_fund(currency: str, amount: Decimal):
        # from binance to bitstamp
        address = settings.BITSTAMP['ACCOUNTS'][currency]
        resp = binance.send_transaction(address, currency, amount)
        return {'id': resp['id'], 'src': EXCHANGE_SITE.binance}

    @staticmethod
    def crypto_transfer_in_fund_to_out_fund(currency: str, amount: Decimal):
        # from coinbase to bitstamp
        address = settings.BITSTAMP['ACCOUNTS'][currency]
        resp = coinbase.send_transaction(address, currency, amount)
        return {'id': resp['id'], 'src': EXCHANGE_SITE.coinbase}

    @staticmethod
    def track_transferring():
        actions = CryptoFundAction.objects.filter(status=CRYPTO_FUND_ACTION_STATUS.transferring)

        list_tx = binance.list_withdraw(30 * 60)
        dict_tx = {tx['id']: tx for tx in list_tx}

        for action in actions:
            try:
                data = simplejson.loads(action.provider_data)
                if data['src'] == EXCHANGE_SITE.binance:
                    tx = dict_tx.get(data.get('id', ''))
                    if tx['status'] == 6:
                        action.status = CRYPTO_FUND_ACTION_STATUS.transferred
                        data['tx_hash'] = tx['txId']
                        action.provider_data = simplejson.dumps(data)
                        action.save()
                else:
                    tx = coinbase.get_transaction(action.currency, data.get('id', ''))
                    if tx.status == 'completed':
                        action.status = CRYPTO_FUND_ACTION_STATUS.transferred
                        action.save()
            except Exception as ex:
                logging.exception(ex)
