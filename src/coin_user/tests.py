from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from coin_system.factories import CountryDefaultConfigFactory
from common.constants import COUNTRY, FIAT_CURRENCY, LANGUAGE
from common.tests.utils import AuthenticationUtils


class ProfileTests(APITestCase):
    def setUp(self):
        self.auth_utils = AuthenticationUtils(self.client)
        self.user = self.auth_utils.create_exchange_user()
        self.auth_utils.login()

    def test_sign_up(self):
        url = reverse('user:profile')
        response = self.client.get(url)
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SignUpTests(APITestCase):
    def setUp(self):
        CountryDefaultConfigFactory(country=COUNTRY.PH, currency=FIAT_CURRENCY.PHP, language=LANGUAGE.en)

    def test_sign_up(self):
        url = reverse('user:sign-up')

        response = self.client.post(url, data={
            'username': 'dev@exchange.com',
            'password': '12345678',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'country': COUNTRY.PH,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
