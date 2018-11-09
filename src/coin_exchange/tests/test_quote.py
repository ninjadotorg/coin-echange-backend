from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from common.constants import CURRENCY, FIAT_CURRENCY


class BankTests(APITestCase):
    def test_invalid(self):
        url = reverse('exchange:quote-detail')
        response = self.client.get(url, data={
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_amount(self):
        url = reverse('exchange:quote-detail')
        response = self.client.get(url, data={
            'amount': '-1'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.json())

    def test_invalid_currency(self):
        url = reverse('exchange:quote-detail')
        response = self.client.get(url, data={
            'currency': 'AAA'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('currency', response.json())

    def test_invalid_fiat_currency(self):
        url = reverse('exchange:quote-detail')
        response = self.client.get(url, data={
            'fiat_currency': 'AAA'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fiat_currency', response.json())

    def test_valid(self):
        url = reverse('exchange:quote-detail')
        response = self.client.get(url, data={
            'amount': '1',
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.VND,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
