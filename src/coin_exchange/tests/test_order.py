from decimal import Decimal
from unittest import TestCase
from unittest.mock import MagicMock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from coin_exchange.business.order import OrderManagement
from coin_exchange.constants import ORDER_TYPE, MIN_ETH_AMOUNT, MIN_BTC_AMOUNT, \
    FEE_COIN_ORDER_BANK, FEE_COIN_ORDER_COD, FEE_COIN_SELLING_ORDER_BANK, ORDER_STATUS
from coin_exchange.exceptions import AmountIsTooSmallException, PriceChangeException
from coin_exchange.factories import OrderFactory, PoolFactory, UserLimitFactory
from coin_exchange.models import Order
from coin_system.constants import FEE_TYPE
from coin_system.factories import FeeFactory
from common.business import PriceManagement, CryptoPrice, RateManagement
from common.constants import DIRECTION, CURRENCY, FIAT_CURRENCY
from common.tests.utils import AuthenticationUtils


class ListOrderTests(APITestCase):
    def setUp(self):
        self.auth_utils = AuthenticationUtils(self.client)
        self.user = self.auth_utils.create_exchange_user()
        self.auth_utils.login()

        OrderFactory.create_batch(10, user=self.user)

    def test_list(self):
        url = reverse('exchange:order-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 10)

    def test_filter_1(self):
        url = reverse('exchange:order-list')
        response = self.client.get(url, data={'direction': DIRECTION.buy}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 5)

    def test_filter_2(self):
        url = reverse('exchange:order-list')
        response = self.client.get(url, data={'order_type': ORDER_TYPE.bank}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 5)


class AddOrderTest(APITestCase):
    def setUp(self):
        PriceManagement.get_cache_price = MagicMock(return_value=CryptoPrice(
            CURRENCY.ETH,
            Decimal('100'),
            Decimal('100'),
        ))
        RateManagement.get_cache_rate = MagicMock(return_value=Decimal('23000'))

        FeeFactory(key=FEE_COIN_ORDER_BANK, value=Decimal('1'), fee_type=FEE_TYPE.percentage)
        FeeFactory(key=FEE_COIN_ORDER_COD, value=Decimal('10'), fee_type=FEE_TYPE.percentage)

        PoolFactory(currency=CURRENCY.ETH, direction=DIRECTION.buy, usage=1, limit=2)

        self.auth_utils = AuthenticationUtils(self.client)
        self.user = self.auth_utils.create_exchange_user()
        self.auth_utils.login()

        UserLimitFactory(fiat_currency=FIAT_CURRENCY.PHP, direction=DIRECTION.buy, usage=0, limit=3000000,
                         user=self.user)

    def test_add_cod_order(self):
        url = reverse('exchange:order-list')
        response = self.client.post(url, data={
            'amount': '1',
            'currency': CURRENCY.ETH,
            'fiat_local_amount': '2530000',
            'fiat_local_currency': FIAT_CURRENCY.PHP,
            'order_type': ORDER_TYPE.cod,
            'direction': DIRECTION.buy,
            'address': '0x6d86cf435978cb75aecc43d0a4e3a379af7667d8',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_bank_order(self):
        url = reverse('exchange:order-list')
        response = self.client.post(url, data={
            'amount': '1',
            'currency': CURRENCY.ETH,
            'fiat_local_amount': '2323000',
            'fiat_local_currency': FIAT_CURRENCY.PHP,
            'order_type': ORDER_TYPE.bank,
            'direction': DIRECTION.buy,
            'address': '0x6d86cf435978cb75aecc43d0a4e3a379af7667d8',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AddSellingOrderTest(APITestCase):
    def setUp(self):
        PriceManagement.get_cache_price = MagicMock(return_value=CryptoPrice(
            CURRENCY.ETH,
            Decimal('100'),
            Decimal('100'),
        ))
        RateManagement.get_cache_rate = MagicMock(return_value=Decimal('23000'))

        FeeFactory(key=FEE_COIN_SELLING_ORDER_BANK, value=Decimal('1'), fee_type=FEE_TYPE.percentage)

        PoolFactory(currency=CURRENCY.ETH, direction=DIRECTION.sell, usage=1, limit=2)

        self.auth_utils = AuthenticationUtils(self.client)
        self.user = self.auth_utils.create_exchange_user()
        self.auth_utils.login()

        UserLimitFactory(fiat_currency=FIAT_CURRENCY.PHP, direction=DIRECTION.sell, usage=0, limit=3000000,
                         user=self.user)

    def test_add_order(self):
        url = reverse('exchange:order-list')
        response = self.client.post(url, data={
            'amount': '1',
            'currency': CURRENCY.ETH,
            'fiat_local_amount': '2323000',
            'fiat_local_currency': FIAT_CURRENCY.PHP,
            'direction': DIRECTION.sell,
            'address': '0x6d86cf435978cb75aecc43d0a4e3a379af7667d8',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class OrderUpdateTest(APITestCase):
    def setUp(self):
        self.auth_utils = AuthenticationUtils(self.client)
        self.user = self.auth_utils.create_exchange_user()
        self.auth_utils.login()

        self.order = OrderFactory(user=self.user, order_type=ORDER_TYPE.cod, status=ORDER_STATUS.pending)

    def test_update_receipt(self):
        order = Order.objects.get(pk=self.order.pk)
        test_receipt = 'SomeReceipt'
        self.assertEqual(order.receipt_url, None)

        url = reverse('exchange:order-receipt', args=[self.order.pk, ])
        response = self.client.put(url, data={
            'receipt_url': test_receipt,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order = Order.objects.get(pk=self.order.pk)
        self.assertEqual(order.receipt_url, test_receipt)


class OrderSupportFunctionTest(TestCase):
    def test_amount_too_small(self):
        with self.assertRaises(AmountIsTooSmallException):
            OrderManagement.check_minimum_amount(MIN_ETH_AMOUNT - Decimal('0.000001'), CURRENCY.ETH)

        with self.assertRaises(AmountIsTooSmallException):
            OrderManagement.check_minimum_amount(MIN_BTC_AMOUNT - Decimal('0.000001'), CURRENCY.BTC)

    def test_check_different_in_threshold(self):
        with self.assertRaises(PriceChangeException):
            OrderManagement.check_different_in_threshold(Decimal(5), Decimal(4.5))
