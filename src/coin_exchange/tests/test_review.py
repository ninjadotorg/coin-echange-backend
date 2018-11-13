from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from coin_exchange.factories import ReviewFactory, OrderFactory
from common.constants import COUNTRY, DIRECTION
from common.tests.utils import AuthenticationUtils


class ReviewTests(APITestCase):
    def setUp(self):
        self.auth_utils = AuthenticationUtils(self.client)
        self.auth_utils.create_exchange_user()

        ReviewFactory.create_batch(10)

    def test_list(self):
        url = reverse('exchange:review-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 10)

    def test_filter(self):
        url = reverse('exchange:review-list')
        response = self.client.get(url, data={'country': COUNTRY.PH}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 5)

    def test_filter_2(self):
        url = reverse('exchange:review-list')
        response = self.client.get(url, data={'direction': DIRECTION.buy}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 5)

    def test_add(self):
        self.auth_utils.login()
        order = OrderFactory()

        url = reverse('exchange:review-list')
        response = self.client.post(url, data={
            'direction': DIRECTION.buy,
            'review': 'Some review',
            'order': order.pk,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
