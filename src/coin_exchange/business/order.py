from decimal import Decimal

from coin_exchange.constants import MIN_ETH_AMOUNT, MIN_BTC_AMOUNT, ORDER_TYPE
from coin_exchange.exceptions import AmountIsTooSmallException
from coin_exchange.serializers import OrderSerializer, SellingOrderSerializer
from coin_user.models import ExchangeUser
from common.constants import DIRECTION, CURRENCY


class OrderManagement(object):
    @staticmethod
    def add_order(user: ExchangeUser, serializer: OrderSerializer):
        safe_data = serializer.validated_data
        amount = safe_data['amount']
        currency = safe_data['currency']

        OrderManagement.check_minimum_amount(amount, currency)

        serializer.save(
            user=user,
            fiat_amount=Decimal('0'),
            fiat_currency='',
            raw_fiat_amount=Decimal('0'),
            price=Decimal('0'),
            direction=DIRECTION.buy,
            duration=30,
            fee=Decimal('0'),
            tx_hash='',
            provider_data='',
            ref_code='',
        )

    @staticmethod
    def add_selling_order(user: ExchangeUser, serializer: SellingOrderSerializer):
        safe_data = serializer.validated_data
        amount = safe_data['amount']
        currency = safe_data['currency']

        OrderManagement.check_minimum_amount(amount, currency)

        serializer.save(
            user=user,
            fiat_amount=Decimal('0'),
            fiat_currency='',
            raw_fiat_amount=Decimal('0'),
            price=Decimal('0'),
            order_type=ORDER_TYPE.bank,
            direction=DIRECTION.sell,
            duration=30,
            fee=Decimal('0'),
            tx_hash='',
            provider_data='',
        )

    @staticmethod
    def check_minimum_amount(amount: Decimal, currency: str):
        if currency == CURRENCY.ETH and amount < MIN_ETH_AMOUNT:
            raise AmountIsTooSmallException
        if currency == CURRENCY.BTC and amount < MIN_BTC_AMOUNT:
            raise AmountIsTooSmallException
