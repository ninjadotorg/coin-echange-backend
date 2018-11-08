from decimal import Decimal

from django.db import models

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
    fee_type = models.CharField(max_length=20, choices=VALUE_TYPE)

    def __str__(self):
        return '%s' % self.key
