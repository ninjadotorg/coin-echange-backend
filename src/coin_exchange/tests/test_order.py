from decimal import Decimal
from unittest import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from coin_exchange.business.order import OrderManagement
from coin_exchange.constants import ORDER_TYPE, MIN_ETH_AMOUNT, MIN_BTC_AMOUNT
from coin_exchange.exceptions import AmountIsTooSmallException
from coin_exchange.factories import OrderFactory
from common.constants import DIRECTION, CURRENCY
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
        self.auth_utils = AuthenticationUtils(self.client)
        self.user = self.auth_utils.create_exchange_user()
        self.auth_utils.login()

    def test_add_order(self):
        url = reverse('exchange:order-list')
        response = self.client.post(url, data={
            'amount': '1',
            'currency': 'ETH',
            'fiat_local_amount': '2323000',
            'fiat_local_currency': 'VND',
            'order_type': 'bank',
            'direction': 'buy',
            'address': 'ACryptoAddress',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AddSellingOrderTest(APITestCase):
    def setUp(self):
        self.auth_utils = AuthenticationUtils(self.client)
        self.user = self.auth_utils.create_exchange_user()
        self.auth_utils.login()

    def test_add_order(self):
        url = reverse('exchange:order-list')
        response = self.client.post(url, data={
            'amount': '1',
            'currency': 'ETH',
            'fiat_local_amount': '2323000',
            'fiat_local_currency': 'VND',
            'order_type': 'bank',
            'direction': 'sell',
            'address': 'ACryptoAddress',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class OrderSupportFunctionTest(TestCase):
    def test_amount_too_small(self):
        with self.assertRaises(AmountIsTooSmallException):
            OrderManagement.check_minimum_amount(MIN_ETH_AMOUNT - Decimal('0.000001'), CURRENCY.ETH)

        with self.assertRaises(AmountIsTooSmallException):
            OrderManagement.check_minimum_amount(MIN_BTC_AMOUNT - Decimal('0.000001'), CURRENCY.BTC)
