from django.db import models

from coin_base.models import TimestampedModel
from coin_exchange.constants import ORDER_STATUS, ORDER_TYPE, PAYMENT_STATUS, TRACKING_ADDRESS_STATUS
from coin_user.models import ExchangeUser
from common import model_fields


class Order(TimestampedModel):
    user = models.ForeignKey(ExchangeUser, related_name='user_orders', on_delete=models.PROTECT)
    user_info = models.TextField(null=True)
    amount = model_fields.CryptoAmountField()
    currency = model_fields.CurrencyField()
    fiat_amount = model_fields.FiatAmountField()
    fiat_currency = model_fields.FiatCurrencyField()
    fiat_local_amount = model_fields.FiatAmountField()
    fiat_local_currency = model_fields.FiatCurrencyField()
    raw_fiat_amount = model_fields.FiatAmountField()
    price = model_fields.FiatAmountField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default=ORDER_STATUS.pending)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE)
    direction = model_fields.DirectionField()
    duration = models.IntegerField(null=True)
    fee = model_fields.FiatAmountField()
    address = model_fields.CryptoHashField()
    tx_hash = model_fields.CryptoHashField(null=True, blank=True)
    provider_data = models.TextField(null=True)
    receipt_url = models.CharField(max_length=500, null=True, blank=True)
    ref_code = models.CharField(max_length=10)
    reviewed = models.BooleanField(default=False)


class Payment(TimestampedModel):
    order = models.ForeignKey(Order, related_name='order_payments', on_delete=models.PROTECT)
    fiat_amount = model_fields.FiatAmountField()
    fiat_currency = model_fields.FiatCurrencyField()
    overspent = model_fields.FiatAmountField()
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)


class PaymentDetail(TimestampedModel):
    payment = models.ForeignKey(Payment, related_name='payment_details', on_delete=models.PROTECT)
    fiat_amount = model_fields.FiatAmountField()
    fiat_currency = model_fields.FiatCurrencyField()


class SellingPayment(TimestampedModel):
    address = models.CharField(max_length=100)
    order = models.ForeignKey(Order, related_name='selling_order_payments', on_delete=models.PROTECT, null=True)
    amount = model_fields.CryptoAmountField()
    currency = model_fields.CurrencyField()
    overspent = model_fields.CryptoAmountField()
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)


class SellingPaymentDetail(TimestampedModel):
    payment = models.ForeignKey(SellingPayment, related_name='selling_payment_details', on_delete=models.PROTECT)
    amount = model_fields.CryptoAmountField()
    currency = model_fields.CurrencyField()
    tx_hash = models.CharField(max_length=100, null=True)


class TrackingAddress(TimestampedModel):
    class Meta:
        unique_together = ('user', 'address', 'currency')

    user = models.ForeignKey(ExchangeUser, related_name='user_addresses', on_delete=models.PROTECT)
    address = model_fields.CryptoHashField()
    currency = model_fields.CurrencyField()
    status = models.CharField(max_length=20, choices=TRACKING_ADDRESS_STATUS, default=TRACKING_ADDRESS_STATUS.created)


class Review(TimestampedModel):
    user = models.ForeignKey(ExchangeUser, related_name='user_reviews', on_delete=models.SET_NULL,
                             null=True, blank=True)
    direction = model_fields.DirectionField()
    review = models.CharField(max_length=500)
    country = model_fields.CountryField()
    visible = models.BooleanField(default=True)
    order = models.OneToOneField(Order, related_name='order_review', on_delete=models.PROTECT,
                                 null=True, blank=True)

    def __str__(self):
        return '%s' % self.user.id


class RefCode(TimestampedModel):
    code = models.CharField(max_length=10, unique=True)
    order = models.OneToOneField(Order, related_name='order_ref_code', on_delete=models.CASCADE)


class Pool(TimestampedModel):
    class Meta:
        unique_together = ('currency', 'direction')

    currency = model_fields.CurrencyField()
    direction = model_fields.DirectionField()
    limit = models.DecimalField(max_digits=30, decimal_places=18)
    usage = models.DecimalField(max_digits=30, decimal_places=18)


class UserLimit(TimestampedModel):
    class Meta:
        unique_together = ('user', 'direction')

    user = models.ForeignKey(ExchangeUser, related_name='user_limit', on_delete=models.CASCADE)
    direction = model_fields.DirectionField()
    limit = models.DecimalField(max_digits=20, decimal_places=4)
    usage = models.DecimalField(max_digits=20, decimal_places=4)
    fiat_currency = model_fields.FiatCurrencyField()
