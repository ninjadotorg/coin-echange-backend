from decimal import Decimal

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty

from common.constants import SUPPORT_CURRENCIES, SUPPORT_FIAT_CURRENCIES


class FiatAmountField(serializers.DecimalField):
    def __init__(self, coerce_to_string=None, max_value=None, min_value=Decimal('0'),
                 localize=False, rounding=None, **kwargs):
        max_digits = 18
        decimal_places = 2
        super(FiatAmountField, self).__init__(max_digits, decimal_places, coerce_to_string=coerce_to_string,
                                              max_value=max_value, min_value=min_value,
                                              localize=localize, rounding=rounding, **kwargs)


class CryptoAmountField(serializers.DecimalField):
    def __init__(self, coerce_to_string=None, max_value=None, min_value=Decimal('0'),
                 localize=False, rounding=None, **kwargs):
        max_digits = 18
        decimal_places = 6
        super(CryptoAmountField, self).__init__(max_digits, decimal_places, coerce_to_string=coerce_to_string,
                                                max_value=max_value, min_value=min_value,
                                                localize=localize, rounding=rounding, **kwargs)


class CryptoCurrencyField(serializers.CharField):
    custom_error_messages = {
        'invalid_value': 'Currency is not supported.',
    }

    def __init__(self, **kwargs):
        super(CryptoCurrencyField, self).__init__(**kwargs)

    def run_validation(self, data=empty):
        value = super(CryptoCurrencyField, self).run_validation(data)

        if value not in SUPPORT_CURRENCIES:
            code = 'invalid_value'
            raise ValidationError(self.custom_error_messages[code], code=code)

        return value


class FiatCurrencyField(serializers.CharField):
    custom_error_messages = {
        'invalid_value': 'Currency is not supported.',
    }

    def __init__(self, **kwargs):
        super(FiatCurrencyField, self).__init__(**kwargs)

    def run_validation(self, data=empty):
        value = super(FiatCurrencyField, self).run_validation(data)

        if value not in SUPPORT_FIAT_CURRENCIES:
            code = 'invalid_value'
            raise ValidationError(self.custom_error_messages[code], code=code)

        return value
