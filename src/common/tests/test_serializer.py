from django.test import TestCase
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from common import serializer_fields
from common.constants import CURRENCY, FIAT_CURRENCY


class TestSerializer(serializers.Serializer):
    currency = serializer_fields.CryptoCurrencyField()
    fiat_currency = serializer_fields.FiatCurrencyField()


class QuoteValidationTests(TestCase):
    def test_invalid_currency(self):
        field = 'currency'
        serializer = TestSerializer(data={
            field: 'AAA',
        })
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            full_details = e.get_full_details()
            self.assertIn(field, full_details)
            self.assertIn(full_details[field][0]['code'], 'invalid_value')

    def test_invalid_fiat_currency(self):
        field = 'fiat_currency'
        serializer = TestSerializer(data={
            field: 'AAA',
        })
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            full_details = e.get_full_details()
            self.assertIn(field, full_details)
            self.assertIn(full_details[field][0]['code'], 'invalid_value')

    def test_valid(self):
        serializer = TestSerializer(data={
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.USD,
        })

        self.assertEqual(serializer.is_valid(False), True)
