from django.db import models

from coin_base.models import TimestampedModel
from coin_exchange.constants import ORDER_STATUS, ORDER_TYPE, PAYMENT_STATUS, TRACKING_ADDRESS_STATUS, \
    TRACKING_TRANSACTION_STATUS, TRACKING_TRANSACTION_DIRECTION, REFERRAL_STATUS, ORDER_USER_PAYMENT_TYPE, \
    CRYPTO_FUND_TYPE, CRYPTO_FUND_ACTION, CRYPTO_FUND_ACTION_STATUS, CRYPTO_TOKEN_PROTOCOL
from coin_user.models import ExchangeUser
from common import model_fields
from common.constants import DIRECTION, DIRECTION_ALL


class Order(TimestampedModel):
    class Meta:
        verbose_name = 'Exch Buying Order'
        verbose_name_plural = 'Exch Buying Orders'

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
    order_user_payment_type = models.CharField(max_length=20, choices=ORDER_USER_PAYMENT_TYPE, null=True, blank=True)
    direction = model_fields.DirectionField()
    duration = models.IntegerField(null=True)
    fee = model_fields.FiatAmountField()
    address = model_fields.CryptoHashField()
    tx_hash = model_fields.CryptoHashField(null=True, blank=True)
    provider_data = models.TextField(null=True)
    receipt_url = models.CharField(max_length=500, null=True, blank=True)
    ref_code = models.CharField(max_length=10)
    reviewed = models.BooleanField(default=False)
    first_purchase = models.BooleanField(default=False)

    def __str__(self):
        return 'Order #{} for {}ing {:.6f} {}'.format(self.id, self.direction, self.amount, self.currency)

    def format_amount(self):
        return '{:.6f}'.format(self.amount)

    format_amount.short_description = 'Amount'

    def _destroy_order(self, status):
        self.status = status
        self.save(update_fields=['status', 'updated_at'])


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
        verbose_name = 'Tracking Address'
        verbose_name_plural = 'Tracking Addresses'

    user = models.ForeignKey(ExchangeUser, related_name='user_addresses', on_delete=models.CASCADE)
    order = models.OneToOneField(Order, related_name='order_address', on_delete=models.CASCADE, null=True, blank=True)
    address = model_fields.CryptoHashField()
    currency = model_fields.CurrencyField()
    status = models.CharField(max_length=20, choices=TRACKING_ADDRESS_STATUS, default=TRACKING_ADDRESS_STATUS.created)


class TrackingTransaction(TimestampedModel):
    class Meta:
        unique_together = ('tx_hash', 'currency')
        verbose_name = 'Tracking Transaction'
        verbose_name_plural = 'Tracking Transactions'

    tx_hash = model_fields.CryptoHashField()
    currency = model_fields.CurrencyField()
    order = models.OneToOneField(Order, related_name='order_tx_hashes', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=TRACKING_TRANSACTION_STATUS,
                              default=TRACKING_TRANSACTION_STATUS.pending)
    direction = models.CharField(max_length=20, choices=TRACKING_TRANSACTION_DIRECTION)
    tracking_address = models.ForeignKey(TrackingAddress, related_name='address_transactions', null=True, blank=True,
                                         on_delete=models.CASCADE)
    to_address = model_fields.CryptoHashField(blank=True)


class Review(TimestampedModel):
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    user = models.ForeignKey(ExchangeUser, related_name='user_reviews', on_delete=models.SET_NULL,
                             null=True, blank=True)
    name = models.CharField(max_length=100, blank=True)
    direction = model_fields.DirectionField()
    review = models.CharField(max_length=500)
    country = model_fields.CountryField()
    visible = models.BooleanField(default=True)
    order = models.OneToOneField(Order, related_name='order_review', on_delete=models.PROTECT,
                                 null=True, blank=True)

    def __str__(self):
        return '%s' % self.name


class RefCode(TimestampedModel):
    code = models.CharField(max_length=10, unique=True)
    order = models.OneToOneField(Order, related_name='order_ref_code', on_delete=models.CASCADE)


class Pool(TimestampedModel):
    class Meta:
        unique_together = ('currency', 'direction')

    currency = model_fields.CurrencyField()
    direction = model_fields.DirectionField()
    limit = model_fields.CryptoAmountField()
    usage = model_fields.CryptoAmountField()

    def __str__(self):
        return '%s - %s' % (DIRECTION[self.direction], self.currency)


class UserLimit(TimestampedModel):
    class Meta:
        unique_together = ('user', 'direction')

    user = models.ForeignKey(ExchangeUser, related_name='user_limit', on_delete=models.CASCADE)
    direction = model_fields.DirectionField()
    limit = model_fields.FiatAmountField()
    usage = model_fields.FiatAmountField()
    fiat_currency = model_fields.FiatCurrencyField()

    def __str__(self):
        return '%s - %s' % (DIRECTION[self.direction] if self.direction != DIRECTION_ALL else 'All', self.fiat_currency)


class ReferralOrder(TimestampedModel):
    class Meta:
        verbose_name = 'Referral Transaction'
        verbose_name_plural = 'Referral Transactions'

    order = models.ForeignKey(Order, related_name='order_referrals', on_delete=models.PROTECT)
    user = models.ForeignKey(ExchangeUser, related_name='user_order_referrals', null=True, on_delete=models.PROTECT)
    amount = model_fields.CryptoAmountField()
    currency = model_fields.CurrencyField()
    status = models.CharField(max_length=20, choices=REFERRAL_STATUS, default=REFERRAL_STATUS.pending)
    referrer = models.BooleanField(default=True)
    address = model_fields.CryptoHashField()
    tx_hash = model_fields.CryptoHashField(null=True)
    provider_data = models.TextField(null=True)

    def format_amount(self):
        return '{:.6f}'.format(self.amount)

    format_amount.short_description = 'Amount'


class PromotionRule(TimestampedModel):
    class Meta:
        verbose_name = 'Promotion Rule'
        verbose_name_plural = 'Promotion Rules'

    country = model_fields.CountryField()
    currency = model_fields.FiatCurrencyField()
    active = models.BooleanField(default=True)
    first_click_count = models.IntegerField(default=0)
    first_click_amount = models.IntegerField(default=0)
    first_click_days = models.IntegerField(default=0)
    first_click_bonus = model_fields.FiatAmountField()
    first_referral_count = models.IntegerField(default=0)
    first_referral_amount = model_fields.FiatAmountField(default=0)
    first_referral_referrer_bonus = model_fields.FiatAmountField(default=0)
    first_referral_referee_bonus = model_fields.FiatAmountField(default=0)
    referrer_percentage = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    referrer_next_duration = models.IntegerField(default=0)
    referrer_percentage_2 = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    referee_percentage = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    referee_next_duration = models.IntegerField(default=0)
    referee_percentage_2 = models.DecimalField(max_digits=7, decimal_places=4, default=0)


class PromotionUser(TimestampedModel):
    user = models.OneToOneField(ExchangeUser, related_name='user_promotion', on_delete=models.PROTECT)
    first_click_count = models.IntegerField(default=0)
    first_click_amount = model_fields.FiatAmountField(default=0)
    first_click_expired = models.DateTimeField(null=True)
    referral_count = models.IntegerField(default=0)
    referral_amount = model_fields.FiatAmountField(default=0)
    currency = model_fields.FiatCurrencyField()


class PromotionOrder(TimestampedModel):
    class Meta:
        verbose_name = 'Promotion Transaction'
        verbose_name_plural = 'Promotion Transactions'

    order = models.ForeignKey(Order, related_name='order_promotions', on_delete=models.PROTECT)
    user = models.ForeignKey(ExchangeUser, related_name='user_order_promotions', null=True, on_delete=models.PROTECT)
    amount = model_fields.FiatAmountField()
    currency = model_fields.FiatCurrencyField()
    status = models.CharField(max_length=20, choices=REFERRAL_STATUS, default=REFERRAL_STATUS.pending)
    referrer = models.BooleanField(default=True)
    note = models.CharField(max_length=200, null=True, blank=True)


class CryptoFund(TimestampedModel):
    class Meta:
        verbose_name = 'Crypto Fund'
        verbose_name_plural = 'Crypto Funds'
        unique_together = ('currency', 'fund_type')

    amount = model_fields.CryptoAmountField()
    currency = model_fields.CurrencyField()
    fund_type = models.CharField(max_length=20, choices=CRYPTO_FUND_TYPE)

    def format_amount(self):
        return '{:.6f} {}'.format(self.amount, self.currency)

    format_amount.short_description = 'Amount'


class CryptoFundAction(TimestampedModel):
    class Meta:
        verbose_name = 'Crypto Fund Action'
        verbose_name_plural = 'Crypto Fund Actions'

    from_amount = model_fields.CryptoAmountField()
    from_currency = model_fields.CurrencyField()
    amount = model_fields.CryptoAmountField()
    currency = model_fields.CurrencyField()
    from_fund_type = models.CharField(max_length=20, choices=CRYPTO_FUND_TYPE, null=True, blank=True)
    fund_type = models.CharField(max_length=20, choices=CRYPTO_FUND_TYPE, null=True, blank=True)
    action = models.CharField(max_length=20, choices=CRYPTO_FUND_ACTION, null=True, blank=True)
    status = models.CharField(max_length=20, choices=CRYPTO_FUND_ACTION_STATUS, null=True, blank=True)
    provider_data = models.TextField(null=True)

    def format_from_amount(self):
        return '{:.6f} {}'.format(self.from_amount, self.from_currency)

    format_from_amount.short_description = 'From Amount'

    def format_amount(self):
        return '{:.6f} {}'.format(self.amount, self.currency)

    format_amount.short_description = 'Amount'


class CryptoToken(models.Model):
    class Meta:
        verbose_name = 'Crypto Token'
        verbose_name_plural = 'Crypto Tokens'

    address = model_fields.CryptoHashField(primary_key=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    symbol = models.CharField(max_length=10, null=True, blank=True)
    protocol = models.CharField(max_length=10, choices=CRYPTO_TOKEN_PROTOCOL)
    decimals = models.IntegerField(default=18)
    auto_price = models.BooleanField()
    buy_price = model_fields.FiatAmountField(null=True, blank=True)
    sell_price = model_fields.FiatAmountField(null=True, blank=True)
    active = models.BooleanField(default=True)
