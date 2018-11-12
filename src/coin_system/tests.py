from decimal import Decimal
from unittest.mock import MagicMock

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from coin_system.business import get_config, get_fee, get_country_default
from coin_system.factories import ConfigFactory, FeeFactory, BankFactory, PopularPlaceFactory, CountryCurrencyFactory, \
    CountryDefaultConfigFactory
from coin_system.models import Config
from common.business import PriceManagement, CryptoPrice, RateManagement
from common.constants import VALUE_TYPE, COUNTRY, FIAT_CURRENCY, CURRENCY


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

    def test_get_country_default(self):
        CountryDefaultConfigFactory(country=COUNTRY.VN, currency=FIAT_CURRENCY.VND, language='vi')

        config1 = get_country_default(COUNTRY.VN)
        self.assertEqual(FIAT_CURRENCY.VND, config1.currency)

        config2 = get_country_default(COUNTRY.VN)
        self.assertEqual(FIAT_CURRENCY.VND, config2.currency)


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


class CountryCurrencyTests(APITestCase):
    def setUp(self):
        CountryCurrencyFactory(active=True, country=COUNTRY.VN, currency=FIAT_CURRENCY.VND)
        CountryCurrencyFactory(active=True, country=COUNTRY.HK, currency=FIAT_CURRENCY.USD)
        CountryCurrencyFactory(active=True, country=COUNTRY.HK, currency=FIAT_CURRENCY.HKD)
        CountryCurrencyFactory(active=False, country=COUNTRY.HK)

    def test_get_1(self):
        url = reverse('system:countrycurrency-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 3)

    def test_get_2(self):
        url = reverse('system:countrycurrency-list')
        response = self.client.get(url, data={'country': COUNTRY.HK}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)


class PopularPlaceTests(APITestCase):
    def setUp(self):
        PopularPlaceFactory(active=True, country=COUNTRY.VN)
        PopularPlaceFactory(active=True, country=COUNTRY.VN)
        PopularPlaceFactory(active=True, country=COUNTRY.HK)
        PopularPlaceFactory(active=False, country=COUNTRY.HK)

    def test_get_1(self):
        url = reverse('system:popularplace-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 3)

    def test_get_2(self):
        url = reverse('system:popularplace-list')
        response = self.client.get(url, data={'country': COUNTRY.VN}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)


class SetupData(APITestCase):
    def setUp(self):
        PriceManagement.save_cache_price = MagicMock(return_value=CryptoPrice(
            CURRENCY.ETH,
            Decimal('100'),
            Decimal('100'),
        ))
        RateManagement.save_rates = MagicMock(return_value=None)

    def test_save_rates(self):
        url = reverse('system:currency-rates')
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_save_cache_price(self):
        url = reverse('system:crypto-rates')
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
