from django.db import models

from coin_base.models import TimestampedModel
from coin_exchange.constants import DIRECTION, CURRENCY, ORDER_STATUS, ORDER_TYPE, COUNTRY, PAYMENT_STATUS, \
    FIAT_CURRENCY
from coin_user.models import ExchangeUser


class Order(TimestampedModel):
    user = models.ForeignKey(ExchangeUser, related_name='user_orders', on_delete=models.PROTECT)
    user_info = models.TextField(null=True)
    amount = models.DecimalField(max_digits=30, decimal_places=18)
    currency = models.CharField(max_length=5, choices=CURRENCY)
    fiat_amount = models.DecimalField(max_digits=20, decimal_places=4)
    fiat_currency = models.CharField(max_length=5, choices=FIAT_CURRENCY)
    fiat_local_amount = models.DecimalField(max_digits=20, decimal_places=4)
    fiat_local_currency = models.CharField(max_length=5)
    raw_fiat_amount = models.DecimalField(max_digits=20, decimal_places=4)
    price = models.DecimalField(max_digits=20, decimal_places=4)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default=ORDER_STATUS.pending)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE)
    direction = models.CharField(max_length=5, choices=DIRECTION)
    duration = models.IntegerField(null=True)
    fee_percentage = models.DecimalField(max_digits=7, decimal_places=4)
    fee = models.DecimalField(max_digits=20, decimal_places=4)
    address = models.CharField(max_length=100)
    tx_hash = models.CharField(max_length=100, null=True)
    provider_data = models.TextField(null=True)
    receipt_url = models.CharField(max_length=500)
    ref_code = models.CharField(max_length=10)
    center = models.CharField(max_length=10)
    reviewed = models.BooleanField(default=False)


class Payment(TimestampedModel):
    order = models.ForeignKey(Order, related_name='order_payments', on_delete=models.PROTECT)
    fiat_amount = models.DecimalField(max_digits=20, decimal_places=4)
    fiat_currency = models.CharField(max_length=5)
    overspent = models.DecimalField(max_digits=20, decimal_places=4)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)


class PaymentDetail(TimestampedModel):
    payment = models.ForeignKey(Payment, related_name='payment_details', on_delete=models.PROTECT)
    fiat_amount = models.DecimalField(max_digits=20, decimal_places=4)
    fiat_currency = models.CharField(max_length=5)


class SellingPayment(TimestampedModel):
    address = models.CharField(max_length=100)
    order = models.ForeignKey(Order, related_name='selling_order_payments', on_delete=models.PROTECT, null=True)
    amount = models.DecimalField(max_digits=30, decimal_places=18)
    currency = models.CharField(max_length=5, choices=CURRENCY)
    overspent = models.DecimalField(max_digits=30, decimal_places=18)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)


class SellingPaymentDetail(TimestampedModel):
    payment = models.ForeignKey(SellingPayment, related_name='selling_payment_details', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=30, decimal_places=18)
    currency = models.CharField(max_length=5, choices=CURRENCY)
    tx_hash = models.CharField(max_length=100, null=True)


class TrackingAddress(TimestampedModel):
    address = models.CharField(max_length=100)
    currency = models.CharField(max_length=5, choices=CURRENCY)


class Review(TimestampedModel):
    class Meta:
        unique_together = ('user', 'order')

    user = models.ForeignKey(ExchangeUser, related_name='user_reviews', on_delete=models.SET_NULL, null=True)
    direction = models.CharField(max_length=10, choices=DIRECTION, null=True)
    review = models.CharField(max_length=500)
    visible = models.BooleanField(default=True)
    order = models.OneToOneField(Order, related_name='order_review', on_delete=models.PROTECT)

    def __str__(self):
        return '%s' % self.user.id


class RefCode(TimestampedModel):
    code = models.CharField(max_length=10, unique=True)
    order = models.OneToOneField(Order, related_name='order_ref_code', on_delete=models.CASCADE)


class Pool(TimestampedModel):
    class Meta:
        unique_together = ('currency', 'direction')

    currency = models.CharField(max_length=5, choices=CURRENCY)
    direction = models.CharField(max_length=5, choices=DIRECTION)
    limit = models.DecimalField(max_digits=30, decimal_places=18)
    usage = models.DecimalField(max_digits=30, decimal_places=18)


class Center(models.Model):
    class Meta:
        unique_together = ('country', 'currency')

    country = models.CharField(max_length=3, choices=COUNTRY)
    currency = models.CharField(max_length=5, choices=CURRENCY)
    account_name = models.CharField(max_length=255, blank=True)
    account_number = models.CharField(max_length=255, blank=True)
    bank_name = models.CharField(max_length=255, blank=True)
    bank_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return '%s (%s)' % (self.country, self.currency)


class UserLimit(TimestampedModel):
    user = models.OneToOneField(ExchangeUser, related_name='user_limit', on_delete=models.CASCADE)
    limit = models.DecimalField(max_digits=20, decimal_places=4)
    usage = models.DecimalField(max_digits=20, decimal_places=4)
    fiat_currency = models.CharField(max_length=5, choices=FIAT_CURRENCY)
