from unittest.mock import MagicMock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from coin_exchange.business.crypto import AddressManagement
from coin_exchange.constants import TRACKING_ADDRESS_STATUS
from coin_exchange.factories import TrackingAddressFactory
from common.constants import CURRENCY
from common.tests.utils import AuthenticationUtils


class CryptoTests(APITestCase):
    def setUp(self):
        self.auth_utils = AuthenticationUtils(self.client)
        self.user = self.auth_utils.create_exchange_user()
        self.auth_utils.login()

        self.test_address = 'AGeneratedCryptoAddress'
        AddressManagement.generate_address = MagicMock(return_value=self.test_address)

    def test_get_existing_address(self):
        obj = TrackingAddressFactory(user=self.user, currency=CURRENCY.ETH, status=TRACKING_ADDRESS_STATUS.created)

        url = reverse('exchange:address-list')
        response = self.client.post(url + '?currency={}'.format(CURRENCY.ETH), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), obj.address)

    def test_create_address(self):
        url = reverse('exchange:address-list')
        response = self.client.post(url + '?currency={}'.format(CURRENCY.ETH), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), self.test_address)
