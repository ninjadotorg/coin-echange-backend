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
    def transfer_in_fund_to_storage(amount: Decimal, currency: str):
        provider_data = FundManagement.crypto_transfer_in_fund_to_storage(amount, currency)

        in_fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.in_fund)
        old_fund_amount = in_fund.amount - amount
        in_fund.amount = F('amount') - amount
        in_fund.save()
        storage_fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.storage_fund)
        new_fund_amount = storage_fund.amount + amount
        storage_fund.amount = F('amount') + amount
        storage_fund.save()

        action = CryptoFundAction.objects.create(
            from_amount=old_fund_amount,
            from_currency=in_fund.currency,
            amount=new_fund_amount,
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
    def transfer_storage_to_out_fund(amount: Decimal, currency: str):
        provider_data = FundManagement.crypto_transfer_storage_to_out_fund(amount, currency)

        out_fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.out_fund)
        old_fund_amount = out_fund.amount + amount
        out_fund.amount = F('amount') + amount
        out_fund.save()
        storage_fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.storage_fund)
        new_fund_amount = storage_fund.amount - amount
        storage_fund.amount = F('amount') - amount
        storage_fund.save()

        action = CryptoFundAction.objects.create(
            from_amount=old_fund_amount,
            from_currency=out_fund.currency,
            amount=new_fund_amount,
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
    def transfer_in_fund_to_out_fund(amount: Decimal, currency: str):
        provider_data = FundManagement.crypto_transfer_in_fund_to_out_fund(amount, currency)

        in_fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.in_fund)
        old_fund_amount = in_fund.amount - amount
        in_fund.amount = F('amount') - amount
        in_fund.save()
        out_fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.out_fund)
        new_fund_amount = out_fund.amount + amount
        out_fund.amount = F('amount') + amount
        out_fund.save()

        action = CryptoFundAction.objects.create(
            from_amount=old_fund_amount,
            from_currency=in_fund.currency,
            amount=new_fund_amount,
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
    def convert_storage_to_vault(amount: Decimal, currency: str):
        provider_data = binance.send_sell_order('{}USDT'.format(currency), amount)
        storage_fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.storage_fund)
        old_fund_amount = storage_fund.amount - amount
        storage_fund.amount = F('amount') - amount
        storage_fund.save()
        vault_fund = CryptoFund.objects.get(currency=CURRENCY.USDT, fund_type=CRYPTO_FUND_TYPE.storage_fund)
        new_fund_amount = vault_fund.amount + amount
        vault_fund.amount = F('amount') + amount
        vault_fund.save()

        action = CryptoFundAction.objects.create(
            from_amount=old_fund_amount,
            from_currency=storage_fund.currency,
            amount=new_fund_amount,
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
    def convert_vault_to_storage(amount: Decimal, currency: str):
        provider_data = binance.send_buy_order('{}USDT'.format(currency), amount)
        storage_fund = CryptoFund.objects.get(currency=CURRENCY.USDT, fund_type=CRYPTO_FUND_TYPE.storage_fund)
        old_fund_amount = storage_fund.amount - amount
        storage_fund.amount = F('amount') - amount
        storage_fund.save()
        vault_fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.storage_fund)
        new_fund_amount = vault_fund.amount + amount
        vault_fund.amount = F('amount') + amount
        vault_fund.save()

        action = CryptoFundAction.objects.create(
            from_amount=old_fund_amount,
            from_currency=storage_fund.currency,
            amount=new_fund_amount,
            currency=vault_fund.currency,
            from_fund_type=CRYPTO_FUND_TYPE.storage_fund,
            fund_type=CRYPTO_FUND_TYPE.storage_fund,
            action=CRYPTO_FUND_ACTION.convert,
            status=CRYPTO_FUND_ACTION_STATUS.converted,
            provider_data=simplejson.dumps(provider_data),
        )

        return action

    @staticmethod
    def crypto_transfer_in_fund_to_storage(amount: Decimal, currency: str):
        # from coinbase to binance
        address = settings.BINANCE['ACCOUNTS'][currency]
        resp = coinbase.send_transaction(address, currency, amount)
        return {'id': resp.id, 'src': EXCHANGE_SITE.coinbase}

    @staticmethod
    def crypto_transfer_storage_to_out_fund(amount: Decimal, currency: str):
        # from binance to bitstamp
        address = settings.BITSTAMP['ACCOUNTS'][currency]
        resp = binance.send_transaction(address, currency, amount)
        return {'id': resp['id'], 'src': EXCHANGE_SITE.binance}

    @staticmethod
    def crypto_transfer_in_fund_to_out_fund(amount: Decimal, currency: str):
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
