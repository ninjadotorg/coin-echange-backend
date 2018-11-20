from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F

from coin_exchange.business.crypto import CryptoTransactionManagement
from coin_exchange.business.quote import QuoteManagement
from coin_exchange.constants import (
    MIN_ETH_AMOUNT,
    MIN_BTC_AMOUNT,
    ORDER_TYPE,
    ORDER_EXPIRATION_DURATION,
    DIFFERENT_THRESHOLD,
    REF_CODE_LENGTH,
    ORDER_STATUS)
from coin_exchange.exceptions import AmountIsTooSmallException, PriceChangeException, InvalidOrderStatusException
from coin_exchange.models import UserLimit, Pool, Order
from coin_exchange.serializers import OrderSerializer, SellingOrderSerializer
from coin_system.business import round_crypto_currency
from common.business import validate_crypto_address, get_now, generate_random_code
from common.constants import DIRECTION, CURRENCY, FIAT_CURRENCY, DIRECTION_ALL
from common.exceptions import InvalidAddress


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
    def add_order(user: User, serializer: OrderSerializer):
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
        serializer.save(
            user=user.exchange_user,
            fiat_amount=check_fiat_amount,
            fiat_currency=FIAT_CURRENCY.USD,
            raw_fiat_amount=quote_data['raw_fiat_amount'],
            price=quote_data['price'],
            direction=direction,
            duration=ORDER_EXPIRATION_DURATION,
            fee=check_fee,
            ref_code=generate_random_code(REF_CODE_LENGTH),
        )

        OrderManagement._increase_limit(user, amount, currency, direction, fiat_local_amount, fiat_local_currency)

    @staticmethod
    @transaction.atomic
    def add_selling_order(user: User, serializer: SellingOrderSerializer):
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

        serializer.save(
            user=user.exchange_user,
            fiat_amount=check_fiat_amount,
            fiat_currency=FIAT_CURRENCY.USD,
            raw_fiat_amount=quote_data['raw_fiat_amount'],
            price=quote_data['price'],
            order_type=ORDER_TYPE.bank,
            direction=DIRECTION.sell,
            status=ORDER_STATUS.transferring,
            fee=check_fee,
            ref_code=generate_random_code(REF_CODE_LENGTH)
        )

        OrderManagement._increase_limit(user, amount, currency, direction, fiat_local_amount, fiat_local_currency)

    @staticmethod
    @transaction.atomic
    def cancel_order(user: User, order: Order):
        if order.status == ORDER_STATUS.pending and order.direction == DIRECTION.buy \
                and order.user.user == user:
            order.status = ORDER_STATUS.cancelled
            order.save()

            OrderManagement._decrease_limit(user, order.amount, order.currency, order.direction,
                                            order.fiat_local_amount, order.fiat_local_currency)
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
    def complete_order(order: Order):
        if order.status == ORDER_STATUS.processing:
            if order.direction == DIRECTION.buy:
                order.status = ORDER_STATUS.transferring
                # Want to save before transfer crypto
                order.save()

                tx_hash, provider_data = CryptoTransactionManagement.transfer(order.address,
                                                                              order.currency, order.amount)
                order.tx_hash = tx_hash
                order.provider_data = provider_data
            else:
                order.status = ORDER_STATUS.success

            order.save()
        else:
            raise InvalidOrderStatusException

    @staticmethod
    @transaction.atomic
    def reject_order(user: User, order: Order):
        if order.user.user == user and order.status == ORDER_STATUS.processing:
            order.status = ORDER_STATUS.rejected
            order.save()

            OrderManagement._decrease_limit(user, order.amount, order.currency, order.direction,
                                            order.fiat_local_amount, order.fiat_local_currency)
        else:
            raise InvalidOrderStatusException

    @staticmethod
    def expire_order():
        now = get_now()
        Order.objects.filter(created_at__lt=now - timedelta(seconds=ORDER_EXPIRATION_DURATION),
                             status=ORDER_STATUS.pending, order_type=ORDER_TYPE.bank,
                             direction=DIRECTION.buy).update(
            status=ORDER_STATUS.expired,
            updated_at=now,
        )

    @staticmethod
    def _increase_limit(user, amount, currency, direction, fiat_local_amount, fiat_local_currency):
        UserLimit.objects.filter(user__user=user,
                                 direction=DIRECTION_ALL,
                                 fiat_currency=fiat_local_currency) \
            .update(usage=F('usage') + fiat_local_amount,
                    updated_at=get_now())
        Pool.objects.filter(direction=direction,
                            currency=currency).update(usage=F('usage') + amount,
                                                      updated_at=get_now())

    @staticmethod
    def _decrease_limit(user, amount, currency, direction, fiat_local_amount, fiat_local_currency):
        user_limit = UserLimit.objects.get(user__user=user,
                                           direction=DIRECTION_ALL,
                                           fiat_currency=fiat_local_currency)
        if user_limit.usage < fiat_local_amount:
            user_limit.usage = 0
        else:
            user_limit.usage = F('usage') - fiat_local_amount
        user_limit.save()

        pool = Pool.objects.get(direction=direction,
                                currency=currency)
        if pool.usage < amount:
            pool.usage = 0
        else:
            pool.usage = F('usage') - amount
        pool.save()

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
        OrderManagement._check_different_in_threshold(fiat_local_amount, check_fiat_local_amount)
        return check_fiat_amount, check_fee, quote_data
