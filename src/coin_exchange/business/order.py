from decimal import Decimal

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F

from coin_exchange.business.quote import QuoteManagement
from coin_exchange.constants import (
    MIN_ETH_AMOUNT,
    MIN_BTC_AMOUNT,
    ORDER_TYPE,
    ORDER_EXPIRATION_DURATION,
    DIFFERENT_THRESHOLD,
    REF_CODE_LENGTH,
)
from coin_exchange.exceptions import AmountIsTooSmallException, PriceChangeException
from coin_exchange.models import UserLimit, Pool
from coin_exchange.serializers import OrderSerializer, SellingOrderSerializer
from coin_system.business import round_crypto_currency
from common.business import validate_crypto_address, get_now, generate_random_code
from common.constants import DIRECTION, CURRENCY, FIAT_CURRENCY
from common.exceptions import InvalidAddress


class OrderManagement(object):
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

        check_fiat_amount, check_fee, quote_data = OrderManagement.validate_data(user, direction,
                                                                                 address, amount, currency,
                                                                                 fiat_local_amount, fiat_local_currency,
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
            ref_code=generate_random_code(REF_CODE_LENGTH),  # TODO Create ref code
        )

        OrderManagement.increase_limit(user, amount, currency, direction, fiat_local_amount, fiat_local_currency)

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

        check_fiat_amount, check_fee, quote_data = OrderManagement.validate_data(user, direction,
                                                                                 address, amount, currency,
                                                                                 fiat_local_amount, fiat_local_currency,
                                                                                 safe_data)

        serializer.save(
            user=user.exchange_user,
            fiat_amount=check_fiat_amount,
            fiat_currency=FIAT_CURRENCY.USD,
            raw_fiat_amount=quote_data['raw_fiat_amount'],
            price=quote_data['price'],
            order_type=ORDER_TYPE.bank,
            direction=DIRECTION.sell,
            fee=check_fee,
            ref_code=generate_random_code(REF_CODE_LENGTH)
        )

        OrderManagement.increase_limit(user, amount, currency, direction, fiat_local_amount, fiat_local_currency)

    @staticmethod
    def increase_limit(user, amount, currency, direction, fiat_local_amount, fiat_local_currency):
        UserLimit.objects.filter(user__user=user,
                                 direction=direction,
                                 fiat_currency=fiat_local_currency) \
            .update(usage=F('usage') + fiat_local_amount,
                    updated_at=get_now())
        Pool.objects.filter(direction=direction,
                            currency=currency).update(usage=F('usage') + amount,
                                                      updated_at=get_now())

    @staticmethod
    def check_minimum_amount(amount: Decimal, currency: str):
        if currency == CURRENCY.ETH and amount < MIN_ETH_AMOUNT:
            raise AmountIsTooSmallException
        if currency == CURRENCY.BTC and amount < MIN_BTC_AMOUNT:
            raise AmountIsTooSmallException

    @staticmethod
    def check_different_in_threshold(amount1: Decimal, amount2: Decimal):
        delta = abs(amount1 - amount2)
        if (delta / max(amount1, amount2)) * Decimal('100') > DIFFERENT_THRESHOLD:
            raise PriceChangeException

    @staticmethod
    def validate_data(user, direction, address, amount, currency, fiat_local_amount, fiat_local_currency, safe_data):
        OrderManagement.check_minimum_amount(amount, currency)
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
        OrderManagement.check_different_in_threshold(fiat_local_amount, check_fiat_local_amount)
        return check_fiat_amount, check_fee, quote_data
