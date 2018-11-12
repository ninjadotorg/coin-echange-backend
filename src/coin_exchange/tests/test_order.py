from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from coin_exchange.constants import ORDER_TYPE
from coin_exchange.factories import OrderFactory
from common.constants import DIRECTION
from common.tests.utils import AuthenticationUtils


class ReviewTests(APITestCase):
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
