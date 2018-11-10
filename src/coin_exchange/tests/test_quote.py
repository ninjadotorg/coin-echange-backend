from decimal import Decimal
from unittest.mock import patch, Mock, MagicMock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from coin_exchange.constants import FEE_COIN_ORDER_BANK, FEE_COIN_ORDER_COD
from coin_system.constants import FEE_TYPE
from coin_system.factories import FeeFactory
from common.business import PriceManagement, RateManagement
from common.constants import CURRENCY, FIAT_CURRENCY


class QuoteValidationTests(APITestCase):
    def setUp(self):
        PriceManagement.get_cache_price = MagicMock(return_value=Decimal('100'))
        RateManagement.get_cache_rate = MagicMock(return_value=Decimal('23000'))

        FeeFactory(key=FEE_COIN_ORDER_BANK, value=Decimal('1'), fee_type=FEE_TYPE.percentage)
        FeeFactory(key=FEE_COIN_ORDER_COD, value=Decimal('10'), fee_type=FEE_TYPE.percentage)

    def test_invalid(self):
        url = reverse('exchange:quote-detail')
        response = self.client.get(url, data={
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crypto_rate(self):
        url = reverse('exchange:quote-detail')
        response = self.client.get(url, data={
            'amount': '1',
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.VND,
        }, format='json')

        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
