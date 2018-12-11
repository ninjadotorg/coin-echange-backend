import uuid
from decimal import Decimal
from unittest.mock import MagicMock

from django.urls import reverse
from rest_framework.test import APITestCase

from coin_exchange.constants import FEE_COIN_ORDER_COD, ORDER_TYPE, FEE_COIN_ORDER_BANK, FEE_COIN_SELLING_ORDER_BANK, \
    FEE_COIN_SELLING_ORDER_COD, ORDER_STATUS
from coin_exchange.factories import PromotionRuleFactory, PoolFactory, UserLimitFactory
from coin_exchange.models import Order, PromotionOrder
from coin_system.constants import FEE_TYPE
from coin_system.factories import FeeFactory
from common.business import PriceManagement, CryptoPrice, RateManagement
from common.constants import CURRENCY, DIRECTION, DIRECTION_ALL, FIAT_CURRENCY
from common.tests.utils import AuthenticationUtils


class PromotionTest(APITestCase):
    def setUp(self):
        self.buy_rate = self.sell_rate = Decimal('100')
        self.fiat_rate = Decimal('1')
        PriceManagement.get_cache_price = MagicMock(return_value=CryptoPrice(
            CURRENCY.ETH,
            self.buy_rate,
            self.sell_rate,
        ))
        RateManagement.get_cache_rate = MagicMock(return_value=self.fiat_rate)

        FeeFactory(key=FEE_COIN_ORDER_BANK, value=Decimal('0'), fee_type=FEE_TYPE.percentage)
        FeeFactory(key=FEE_COIN_ORDER_COD, value=Decimal('0'), fee_type=FEE_TYPE.percentage)
        FeeFactory(key=FEE_COIN_SELLING_ORDER_BANK, value=Decimal('0'), fee_type=FEE_TYPE.percentage)
        FeeFactory(key=FEE_COIN_SELLING_ORDER_COD, value=Decimal('0'), fee_type=FEE_TYPE.percentage)

        PoolFactory(currency=CURRENCY.ETH, direction=DIRECTION.buy, usage=0, limit=100)
        PoolFactory(currency=CURRENCY.ETH, direction=DIRECTION.sell, usage=0, limit=100)

        self.auth_utils = AuthenticationUtils(self.client)
        self.referral = self.auth_utils.create_exchange_user('referral_user')

        self.user = self.auth_utils.create_exchange_user(None, self.referral)
        self.auth_utils.login()

        UserLimitFactory(fiat_currency=self.user.currency, direction=DIRECTION_ALL, usage=0, limit=5000,
                         user=self.user)

    def _make_buy_order(self, amount: Decimal):
        url = reverse('exchange:order-list')
        response = self.client.post(url, data={
            'amount': amount,
            'currency': CURRENCY.ETH,
            'fiat_local_amount': amount * self.buy_rate * self.fiat_rate,
            'fiat_local_currency': FIAT_CURRENCY.PHP,
            'order_type': ORDER_TYPE.cod,
            'direction': DIRECTION.buy,
            'address': uuid.uuid4(),
        }, format='json')
        data = response.json()

        return data['id']

    def _make_sell_order(self, amount: Decimal):
        url = reverse('exchange:order-list')
        response = self.client.post(url, data={
            'amount': amount,
            'currency': CURRENCY.ETH,
            'fiat_local_amount': amount * self.buy_rate * self.fiat_rate,
            'fiat_local_currency': FIAT_CURRENCY.PHP,
            'direction': DIRECTION.sell,
            'order_type': ORDER_TYPE.bank,
            'address': uuid.uuid4(),
        }, format='json')
        data = response.json()

        return data['id']

    def test_add_promotion_for_buying(self):
        PromotionRuleFactory()

        order_id = self._make_buy_order(Decimal('10'))
        order = Order.objects.get(id=order_id)
        order.status = ORDER_STATUS.success
        order.save(update_fields=['status', ])

        ref1 = PromotionOrder.objects.filter(order=order, user=self.referral).first()
        ref2 = PromotionOrder.objects.filter(order=order, user=self.user).first()

        self.assertEqual(ref1.amount, Decimal('100'))
        self.assertEqual(ref2.amount, Decimal('10'))

    def test_add_promotion_for_selling(self):
        PromotionRuleFactory()

        order_id = self._make_sell_order(Decimal('10'))
        order = Order.objects.get(id=order_id)
        order.status = ORDER_STATUS.success
        order.save(update_fields=['status', ])

        ref1 = PromotionOrder.objects.filter(order=order, user=self.referral).first()
        ref2 = PromotionOrder.objects.filter(order=order, user=self.user).first()

        self.assertEqual(ref1.amount, Decimal('100'))
        self.assertEqual(ref2.amount, Decimal('10'))

    def test_add_promotion_without_referee(self):
        PromotionRuleFactory(first_referral_referee_bonus=0)

        order_id = self._make_sell_order(Decimal('10'))
        order = Order.objects.get(id=order_id)
        order.status = ORDER_STATUS.success
        order.save(update_fields=['status', ])

        ref1 = PromotionOrder.objects.filter(order=order, user=self.referral).first()
        ref2 = PromotionOrder.objects.filter(order=order, user=self.user).first()

        self.assertIsNotNone(ref1)
        self.assertIsNone(ref2)

    def test_add_promotion_for_buying_multiple_1(self):
        PromotionRuleFactory()

        order_id = self._make_sell_order(Decimal('7'))
        order = Order.objects.get(id=order_id)
        order.status = ORDER_STATUS.success
        order.save(update_fields=['status', ])

        ref1 = PromotionOrder.objects.filter(order=order, user=self.referral).first()
        ref2 = PromotionOrder.objects.filter(order=order, user=self.user).first()
        self.assertIsNone(ref1)
        self.assertIsNone(ref2)

        order_id = self._make_sell_order(Decimal('3'))
        order = Order.objects.get(id=order_id)
        order.status = ORDER_STATUS.success
        order.save(update_fields=['status', ])

        ref1 = PromotionOrder.objects.filter(order=order, user=self.referral).first()
        ref2 = PromotionOrder.objects.filter(order=order, user=self.user).first()
        self.assertIsNotNone(ref1)
        self.assertIsNotNone(ref2)

    def test_add_promotion_for_buying_multiple_2(self):
        PromotionRuleFactory()

        order_id = self._make_sell_order(Decimal('7'))
        order = Order.objects.get(id=order_id)
        order.status = ORDER_STATUS.success
        order.save(update_fields=['status', ])

        ref1 = PromotionOrder.objects.filter(order=order, user=self.referral).first()
        ref2 = PromotionOrder.objects.filter(order=order, user=self.user).first()
        self.assertIsNone(ref1)
        self.assertIsNone(ref2)

        order_id = self._make_sell_order(Decimal('3'))
        order = Order.objects.get(id=order_id)
        order.status = ORDER_STATUS.success
        order.save(update_fields=['status', ])

        ref1 = PromotionOrder.objects.filter(order=order, user=self.referral).first()
        ref2 = PromotionOrder.objects.filter(order=order, user=self.user).first()
        self.assertIsNotNone(ref1)
        self.assertIsNotNone(ref2)

        order_id = self._make_sell_order(Decimal('1'))
        order = Order.objects.get(id=order_id)
        order.status = ORDER_STATUS.success
        order.save(update_fields=['status', ])

        ref1 = PromotionOrder.objects.filter(order=order, user=self.referral).first()
        ref2 = PromotionOrder.objects.filter(order=order, user=self.user).first()
        self.assertIsNone(ref1)
        self.assertIsNone(ref2)

    def test_add_promotion_for_buying_multiple_3(self):
        PromotionRuleFactory()

        # Not enough for promotion
        order_id = self._make_sell_order(Decimal('7'))
        order = Order.objects.get(id=order_id)
        order.status = ORDER_STATUS.success
        order.save(update_fields=['status', ])
        self.assertEqual(order.first_purchase, True)

        ref1 = PromotionOrder.objects.filter(order=order, user=self.referral).first()
        ref2 = PromotionOrder.objects.filter(order=order, user=self.user).first()
        self.assertIsNone(ref1)
        self.assertIsNone(ref2)

        # It's enough for promotion
        order_id = self._make_sell_order(Decimal('3'))
        order = Order.objects.get(id=order_id)
        order.status = ORDER_STATUS.success
        order.save(update_fields=['status', ])
        self.assertEqual(order.first_purchase, False)

        ref1 = PromotionOrder.objects.filter(order=order, user=self.referral).first()
        ref2 = PromotionOrder.objects.filter(order=order, user=self.user).first()
        self.assertIsNotNone(ref1)
        self.assertIsNotNone(ref2)

        # Only for first time
        order_id = self._make_sell_order(Decimal('1'))
        order = Order.objects.get(id=order_id)
        order.status = ORDER_STATUS.success
        order.save(update_fields=['status', ])
        self.assertEqual(order.first_purchase, False)

        ref1 = PromotionOrder.objects.filter(order=order, user=self.referral).first()
        ref2 = PromotionOrder.objects.filter(order=order, user=self.user).first()
        self.assertIsNone(ref1)
        self.assertIsNone(ref2)
