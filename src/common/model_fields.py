from django.db import models

from common.constants import CURRENCY, FIAT_CURRENCY, COUNTRY, LANGUAGE, DIRECTION


class CurrencyField(models.CharField):
    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 5
        if 'choices' not in kwargs:
            kwargs['choices'] = CURRENCY
        super().__init__(*args, **kwargs)


class FiatCurrencyField(models.CharField):
    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 5
        if 'choices' not in kwargs:
            kwargs['choices'] = FIAT_CURRENCY
        super().__init__(*args, **kwargs)


class CountryField(models.CharField):
    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 3
        if 'choices' not in kwargs:
            kwargs['choices'] = COUNTRY
        super().__init__(*args, **kwargs)


class LanguageField(models.CharField):
    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 10
        if 'choices' not in kwargs:
            kwargs['choices'] = LANGUAGE
        super().__init__(*args, **kwargs)


class DirectionField(models.CharField):
    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 5
        if 'choices' not in kwargs:
            kwargs['choices'] = DIRECTION
        super().__init__(*args, **kwargs)


class CryptoHashField(models.CharField):
    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 255
        super().__init__(*args, **kwargs)


class CryptoAmountField(models.DecimalField):
    def __init__(self, verbose_name=None, name=None, max_digits=None,
                 decimal_places=None, **kwargs):

        if max_digits is None:
            max_digits = 30
        if decimal_places is None:
            decimal_places = 18

        super().__init__(verbose_name=verbose_name, name=name, max_digits=max_digits,
                         decimal_places=decimal_places, **kwargs)


class FiatAmountField(models.DecimalField):
    def __init__(self, verbose_name=None, name=None, max_digits=None,
                 decimal_places=None, **kwargs):

        if max_digits is None:
            max_digits = 18
        if decimal_places is None:
            decimal_places = 2

        super().__init__(verbose_name=verbose_name, name=name, max_digits=max_digits,
                         decimal_places=decimal_places, **kwargs)
