from decimal import Decimal

from coin_exchange.serializers import OrderSerializer, SellingOrderSerializer
from coin_user.models import ExchangeUser
from common.constants import DIRECTION


class OrderManagement(object):
    @staticmethod
    def add_order(user: ExchangeUser, serializer: OrderSerializer):
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
        serializer.save(
            user=user,
            fiat_amount=Decimal('0'),
            fiat_currency='',
            raw_fiat_amount=Decimal('0'),
            price=Decimal('0'),
            direction=DIRECTION.sell,
            duration=30,
            fee=Decimal('0'),
            tx_hash='',
            provider_data='',
        )
