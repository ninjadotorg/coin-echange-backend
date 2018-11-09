from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from coin_system.business import get_config, get_fee
from coin_system.factories import ConfigFactory, FeeFactory, BankFactory
from coin_system.models import Config
from common.constants import VALUE_TYPE, COUNTRY, FIAT_CURRENCY


class ConfigValueTypeTest(TestCase):
    def setUp(self):
        self.key = 'KEY'

    def test_get_int(self):
        ConfigFactory(key=self.key, value='10', value_type=VALUE_TYPE.int)
        config = Config.objects.get(pk=self.key)

        value = config.get_value()
        self.assertEqual(type(value), int)
        self.assertEqual(value, 10)

    def test_get_decimal(self):
        ConfigFactory(key=self.key, value='10.005', value_type=VALUE_TYPE.decimal)
        config = Config.objects.get(pk=self.key)

        value = config.get_value()
        self.assertEqual(type(value), Decimal)
        self.assertEqual(value, Decimal('10.005'))

    def test_get_string(self):
        text = 'Some string'
        ConfigFactory(key=self.key, value=text, value_type=VALUE_TYPE.string)
        config = Config.objects.get(pk=self.key)

        value = config.get_value()
        self.assertEqual(type(value), str)
        self.assertEqual(value, text)


class GetterTests(TestCase):
    def test_get_config(self):
        key = 'KEY'
        value = 'value'

        ConfigFactory(key=key, value=value, value_type=VALUE_TYPE.string)

        config1 = get_config(key)
        config1_value = config1.get_value()
        self.assertEqual(value, config1_value)

        config2 = get_config(key)
        config2_value = config2.get_value()
        self.assertEqual(value, config2_value)

    def test_get_fee(self):
        key = 'KEY'
        value = Decimal('10.5')

        FeeFactory(key=key, value=value)

        fee1 = get_fee(key)
        self.assertEqual(value, fee1.value)

        fee2 = get_fee(key)
        self.assertEqual(value, fee2.value)


class BankTests(APITestCase):
    def setUp(self):
        BankFactory(active=True, country='US', currency='USD')
        BankFactory(active=True, country=COUNTRY.VN, currency=FIAT_CURRENCY.VND)
        BankFactory(active=True, country=COUNTRY.HK, currency=FIAT_CURRENCY.HKD)
        BankFactory(active=True, country=COUNTRY.HK, currency=FIAT_CURRENCY.USD)
        BankFactory(active=False, country='FR', currency='EUR')

    def test_get_1(self):
        url = reverse('system:bank-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 4)

    def test_get_2(self):
        url = reverse('system:bank-list')
        response = self.client.get(url, data={'country': COUNTRY.HK}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_get_3(self):
        url = reverse('system:bank-list')
        response = self.client.get(url, data={'country': COUNTRY.HK, 'currency': FIAT_CURRENCY.HKD}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
