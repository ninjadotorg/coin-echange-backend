import logging

import simplejson
from datetime import timedelta
from decimal import Decimal

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F, Q
from requests import Timeout

from coin_exchange.business.crypto import CryptoTransactionManagement
from coin_exchange.business.quote import QuoteManagement
from coin_exchange.constants import (
    MIN_ETH_AMOUNT,
    MIN_BTC_AMOUNT,
    ORDER_TYPE,
    ORDER_EXPIRATION_DURATION,
    DIFFERENT_THRESHOLD,
    REF_CODE_LENGTH,
    ORDER_STATUS, ORDER_USER_PAYMENT_TYPE)
from coin_exchange.exceptions import AmountIsTooSmallException, PriceChangeException, InvalidOrderStatusException
from coin_exchange.models import UserLimit, Pool, Order
from coin_exchange.serializers import OrderSerializer, SellingOrderSerializer
from coin_system.business import round_crypto_currency
from common.business import validate_crypto_address, get_now, generate_random_code, RateManagement
from common.constants import DIRECTION, CURRENCY, FIAT_CURRENCY, DIRECTION_ALL
from common.exceptions import InvalidAddress, InvalidInputDataException
from common.provider_data import ProviderData
from integration import bitstamp


class OrderManagement(object):
    # Buy - bank
    # PENDING > FIAT_TRANSFERRING > PROCESSING > TRANSFERRING > SUCCESS
    #         > CANCELLED
    #         > EXPIRED
    #                                          > TRANSFER_FAILED > TRANSFERRING
    #                                          > REJECTED
    # Buy - cod
    # PENDING > PROCESSING > TRANSFERRING > SUCCESS
    #         > CANCELLED
    #                      > REJECTED
    #                      > ? CANCELLED
    # Sell - bank
    # TRANSFERRING > TRANSFERRED > PROCESSING > SUCCESS
    #                                         > REJECTED

    @staticmethod
    @transaction.atomic
    def add_order(user: User, serializer: OrderSerializer) -> Order:
        safe_data = serializer.validated_data
        amount = safe_data['amount']
        currency = safe_data['currency']
        address = safe_data['address']
        fiat_local_amount = safe_data['fiat_local_amount']
        fiat_local_currency = safe_data['fiat_local_currency']
        direction = DIRECTION.buy

        check_fiat_amount, check_fee, quote_data = OrderManagement._validate_data(user, direction,
                                                                                  address, amount, currency,
                                                                                  fiat_local_amount,
                                                                                  fiat_local_currency,
                                                                                  safe_data)
        order = serializer.save(
            user=user.exchange_user,
            fiat_amount=check_fiat_amount,
            fiat_currency=FIAT_CURRENCY.USD,
            raw_fiat_amount=quote_data['raw_fiat_amount'],
            price=quote_data['price'],
            direction=direction,
            duration=ORDER_EXPIRATION_DURATION,
            fee=check_fee,
            ref_code=generate_random_code(REF_CODE_LENGTH),
            first_purchase=True if user.exchange_user.first_purchase else False,
        )
        return order

    @staticmethod
    @transaction.atomic
    def add_selling_order(user: User, serializer: SellingOrderSerializer) -> Order:
        safe_data = serializer.validated_data
        amount = safe_data['amount']
        currency = safe_data['currency']
        address = safe_data['address']
        fiat_local_amount = safe_data['fiat_local_amount']
        fiat_local_currency = safe_data['fiat_local_currency']
        direction = DIRECTION.sell

        check_fiat_amount, check_fee, quote_data = OrderManagement._validate_data(user, direction,
                                                                                  address, amount, currency,
                                                                                  fiat_local_amount,
                                                                                  fiat_local_currency,
                                                                                  safe_data)

        order = serializer.save(
            user=user.exchange_user,
            fiat_amount=check_fiat_amount,
            fiat_currency=FIAT_CURRENCY.USD,
            raw_fiat_amount=quote_data['raw_fiat_amount'],
            price=quote_data['price'],
            direction=DIRECTION.sell,
            status=ORDER_STATUS.transferring,
            fee=check_fee,
            ref_code=generate_random_code(REF_CODE_LENGTH),
            first_purchase=True if user.exchange_user.first_purchase else False,
        )
        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(user: User, order: Order):
        if order.status == ORDER_STATUS.pending and order.direction == DIRECTION.buy \
                and order.user.user == user:
            order.status = ORDER_STATUS.cancelled
            order.save(update_fields=['status', 'updated_at'])
        else:
            raise InvalidOrderStatusException

    @staticmethod
    def process_order(order: Order):
        is_able_to_process = False
        if order.direction == DIRECTION.buy and order.order_type == ORDER_TYPE.bank and \
                order.status in [ORDER_STATUS.fiat_transferring, ]:
            is_able_to_process = True
        elif order.direction == DIRECTION.buy and order.order_type == ORDER_TYPE.cod and \
                order.status in [ORDER_STATUS.pending, ]:
            is_able_to_process = True
        elif order.direction == DIRECTION.sell and \
                order.status in [ORDER_STATUS.transferred, ]:
            is_able_to_process = True

        if is_able_to_process:
            order.status = ORDER_STATUS.processing
            order.save()
        else:
            raise InvalidOrderStatusException

    @staticmethod
    @transaction.atomic
    def complete_order(order: Order):
        if order.status == ORDER_STATUS.processing:
            order.first_purchase = True
            if order.direction == DIRECTION.buy:
                order.status = ORDER_STATUS.transferring
                tx_hash, provider_data = CryptoTransactionManagement.transfer(order.address,
                                                                              order.currency,
                                                                              order.amount)
                order.tx_hash = tx_hash
                order.provider_data = provider_data
            else:
                order.status = ORDER_STATUS.success

            order.save(update_fields=['status', 'tx_hash', 'provider_data', 'updated_at'])
        else:
            raise InvalidOrderStatusException

    @staticmethod
    @transaction.atomic
    def reject_order(order: Order):
        if order.status == ORDER_STATUS.processing:
            order.status = ORDER_STATUS.rejected
            order.save(update_fields=['status', 'updated_at'])
        else:
            raise InvalidOrderStatusException

    @staticmethod
    @transaction.atomic
    def expire_order():
        now = get_now()
        orders = Order.objects.filter(created_at__lt=now - timedelta(seconds=ORDER_EXPIRATION_DURATION),
                                      status=ORDER_STATUS.pending, order_type=ORDER_TYPE.bank,
                                      direction=DIRECTION.buy)
        for order in orders:
            order.status = ORDER_STATUS.expired
            order.save(update_fields=['status', 'updated_at'])

    @staticmethod
    def reset_user_limit():
        UserLimit.objects.filter(direction=DIRECTION_ALL).update(usage=0, updated_at=get_now())

    @staticmethod
    def increase_limit(user, amount, currency, direction, fiat_local_amount, fiat_local_currency):
        # Convert local currency to user currency
        update_amount = fiat_local_amount
        if user.currency != fiat_local_currency:
            update_amount = RateManagement.convert_currency(update_amount, fiat_local_currency, user.currency)
        UserLimit.objects.filter(user=user,
                                 direction=DIRECTION_ALL,
                                 fiat_currency=user.currency) \
            .update(usage=F('usage') + update_amount,
                    updated_at=get_now())

        Pool.objects.filter(direction=direction,
                            currency=currency).update(usage=F('usage') + amount,
                                                      updated_at=get_now())

    @staticmethod
    def decrease_limit(user, amount, currency, direction, fiat_local_amount, fiat_local_currency):
        # Convert local currency to user currency
        update_amount = fiat_local_amount
        if user.currency != fiat_local_currency:
            update_amount = RateManagement.convert_currency(update_amount, fiat_local_currency, user.currency)

        user_limit = UserLimit.objects.get(user=user,
                                           direction=DIRECTION_ALL,
                                           fiat_currency=user.currency)
        if user_limit.usage < update_amount:
            user_limit.usage = 0
        else:
            user_limit.usage = F('usage') - update_amount
        user_limit.save()

        pool = Pool.objects.get(direction=direction,
                                currency=currency)
        if pool.usage < amount:
            pool.usage = 0
        else:
            pool.usage = F('usage') - amount
        pool.save()

    @staticmethod
    def load_transferring_order_to_track():
        orders = Order.objects.filter(Q(tx_hash='') | Q(tx_hash__isnull=True),
                                      direction=DIRECTION.buy, status=ORDER_STATUS.transferring)

        list_tx = bitstamp.list_withdrawal_requests(30 * 60)
        dict_tx = {tx['id']: tx for tx in list_tx}

        for order in orders:
            try:
                data = ProviderData(None, order.provider_data).from_json()
                tx = dict_tx.get(data.get('tx_id', ''))
                if tx:
                    order.tx_hash = tx.get('transaction_id', '')
                    order.save(update_fields=['status', 'tx_hash', 'updated_at'])
            except Exception as ex:
                logging.exception(ex)

    @staticmethod
    def _check_minimum_amount(amount: Decimal, currency: str):
        if currency == CURRENCY.ETH and amount < MIN_ETH_AMOUNT:
            raise AmountIsTooSmallException
        if currency == CURRENCY.BTC and amount < MIN_BTC_AMOUNT:
            raise AmountIsTooSmallException

    @staticmethod
    def _check_different_in_threshold(amount1: Decimal, amount2: Decimal):
        delta = abs(amount1 - amount2)
        if (delta / max(amount1, amount2)) * Decimal('100') > DIFFERENT_THRESHOLD:
            raise PriceChangeException

    @staticmethod
    def _validate_data(user, direction, address, amount, currency, fiat_local_amount, fiat_local_currency, safe_data):
        OrderManagement._check_minimum_amount(amount, currency)
        if not validate_crypto_address(currency, address):
            raise InvalidAddress

        quote_data = QuoteManagement.get_quote(user, {
            'amount': round_crypto_currency(amount),
            'currency': currency,
            'fiat_currency': fiat_local_currency,
            'check': True,
            'user_check': True,
            'direction': direction,
        }).data
        check_fiat_amount = Decimal(quote_data['fiat_amount'])
        check_fiat_local_amount = Decimal(quote_data['fiat_local_amount'])
        check_fee = Decimal(quote_data['fee'])
        if direction == DIRECTION.buy and safe_data['order_type'] == ORDER_TYPE.cod:
            check_fiat_amount = Decimal(quote_data['fiat_amount_cod'])
            check_fiat_local_amount = Decimal(quote_data['fiat_local_amount_cod'])
            check_fee = Decimal(quote_data['fee_cod'])
        if direction == DIRECTION.sell:
            if safe_data.get('user_info'):
                user_info = simplejson.loads(safe_data['user_info'])
                if safe_data['order_user_payment_type'] == ORDER_USER_PAYMENT_TYPE.tng:
                    # Make sure
                    if user.exchange_user.phone_number != user_info.get('bankUserPhoneNumber'):
                        raise InvalidInputDataException

        OrderManagement._check_different_in_threshold(fiat_local_amount, check_fiat_local_amount)
        return check_fiat_amount, check_fee, quote_data

    @staticmethod
    def send_new_order_notification(order: Order):
        if settings.UNIT_TEST:
            return

        url = settings.NOTIFICATION_API + '/new-order-notification/'
        try:
            requests.post(url, json={
                'order_type': order.order_type,
                'direction': order.direction,
                'ref_code': order.ref_code,
                'id': order.id,
            }, headers={'Content-type': 'application/json'}, timeout=200)
        except Timeout:
            pass
        except Exception as ex:
            logging.error(ex)
