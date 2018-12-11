from decimal import Decimal

from django.db import models

from coin_base.models import TimestampedModel
from coin_system.constants import FEE_TYPE
from common import model_fields
from common.constants import VALUE_TYPE


class Config(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    value = models.CharField(max_length=255)
    value_type = models.CharField(max_length=20, choices=VALUE_TYPE)

    def get_value(self):
        if self.value_type == VALUE_TYPE.int:
            return int(self.value)
        if self.value_type == VALUE_TYPE.decimal:
            return Decimal(self.value)

        return self.value

    def __str__(self):
        return '%s' % self.key


class Fee(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    value = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE, default=FEE_TYPE.percentage)

    def __str__(self):
        return '%s' % self.key


class Bank(models.Model):
    class Meta:
        unique_together = ('country', 'currency')

    country = model_fields.CountryField()
    currency = model_fields.FiatCurrencyField()
    account_name = models.CharField(max_length=255, blank=True)
    account_number = models.CharField(max_length=255, blank=True)
    bank_name = models.CharField(max_length=255, blank=True)
    bank_id = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return '%s - %s (%s)' % (self.bank_name, self.country, self.currency)


class CountryCurrency(models.Model):
    class Meta:
        unique_together = ('country', 'currency')
        verbose_name = 'Country Currency'
        verbose_name_plural = 'Country Currencies'

    country = model_fields.CountryField()
    currency = model_fields.FiatCurrencyField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return '%s - %s' % (self.country, self.currency)


class PopularPlace(models.Model):
    class Meta:
        verbose_name = 'Popular Place'
        verbose_name_plural = 'Popular Places'

    country = model_fields.CountryField()
    language = model_fields.LanguageField(null=True, blank=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=500, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.country)


class PopularBank(models.Model):
    class Meta:
        verbose_name = 'Popular Bank'
        verbose_name_plural = 'Popular Banks'

    country = model_fields.CountryField()
    language = model_fields.LanguageField(null=True, blank=True)
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.country)


class CountryDefaultConfig(models.Model):
    class Meta:
        verbose_name = 'Country Default Config'
        verbose_name_plural = 'Country Default Configs'

    country = model_fields.CountryField(primary_key=True)
    country_name = models.CharField(max_length=50, blank=True)
    phone_country_code = models.CharField(max_length=5, blank=True)
    language = model_fields.LanguageField()
    currency = model_fields.FiatCurrencyField()
    active = models.BooleanField(default=True)


class LandingPageContact(TimestampedModel):
    class Meta:
        verbose_name = 'Landing Page Contact'
        verbose_name_plural = 'Landing Page Contacts'

    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    description = models.TextField(blank=True)

    def __str__(self):
        return '%s' % self.name
