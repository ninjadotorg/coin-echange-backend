from django.test import TestCase
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from common import serializer_fields
from common.constants import CURRENCY, FIAT_CURRENCY, DIRECTION


class TestSerializer(serializers.Serializer):
    currency = serializer_fields.CryptoCurrencyField()
    fiat_currency = serializer_fields.FiatCurrencyField()
    direction = serializer_fields.DirectionField()


class QuoteValidationTests(TestCase):
    def test_invalid(self):
        for field in ['currency', 'fiat_currency', 'direction']:
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
                self.assertEqual(full_details[field][0]['code'], 'invalid')

    def test_valid(self):
        serializer = TestSerializer(data={
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.USD,
            'direction': DIRECTION.buy,
        })

        self.assertEqual(serializer.is_valid(False), True)
