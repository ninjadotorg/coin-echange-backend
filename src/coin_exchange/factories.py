from decimal import Decimal

import factory

from coin_exchange.constants import ORDER_TYPE, TRACKING_ADDRESS_STATUS
from coin_user.factories import ExchangeUserFactory
from common.constants import CURRENCY, DIRECTION, COUNTRY, FIAT_CURRENCY


class PoolFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_exchange.Pool'


class UserLimitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_exchange.UserLimit'

    user = factory.SubFactory(ExchangeUserFactory)


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_exchange.Order'

    user = factory.SubFactory(ExchangeUserFactory)
    user_info = 'Some user info'
    amount = factory.Iterator([Decimal(i) for i in range(1, 6)])
    currency = CURRENCY.ETH
    fiat_amount = factory.LazyAttribute(lambda o: o.raw_fiat_amount * Decimal('1.01'))
    fiat_currency = FIAT_CURRENCY.USD
    fiat_local_amount = factory.LazyAttribute(lambda o: o.fiat_amount * Decimal('23000'))
    fiat_local_currency = FIAT_CURRENCY.PHP
    raw_fiat_amount = factory.LazyAttribute(lambda o: o.amount * o.price)
    price = Decimal('100')
    order_type = factory.Iterator([ORDER_TYPE.bank, ORDER_TYPE.cod])
    direction = factory.Iterator([DIRECTION.buy, DIRECTION.sell])
    duration = 0
    fee = factory.LazyAttribute(lambda o: o.raw_fiat_amount * o.fiat_amount)
    address = factory.Sequence(lambda n: "CryptoAddress%03d" % n)
    ref_code = 'SomeRefCode'


class TrackingAddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_exchange.TrackingAddress'

    user = factory.SubFactory(ExchangeUserFactory)
    currency = factory.Iterator([CURRENCY.ETH, CURRENCY.BTC])
    address = factory.Sequence(lambda n: "CryptoAddress%03d" % n)
    status = factory.Iterator([
        TRACKING_ADDRESS_STATUS.created,
        TRACKING_ADDRESS_STATUS.has_order,
        TRACKING_ADDRESS_STATUS.has_payment,
        TRACKING_ADDRESS_STATUS.completed,
    ])


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_exchange.Review'

    user = factory.SubFactory(ExchangeUserFactory)
    order = factory.SubFactory(OrderFactory)
    country = factory.Iterator([COUNTRY.KH, COUNTRY.PH])
    direction = factory.Iterator([DIRECTION.buy, DIRECTION.sell])
    review = factory.Sequence(lambda n: "Review %03d" % n)


class PromotionRuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_exchange.PromotionRule'

    country = COUNTRY.PH
    currency = FIAT_CURRENCY.PHP
    active = True
    first_click_count = 0
    first_click_amount = 0
    first_click_days = 0
    first_click_bonus = 0
    first_referral_count = -1
    first_referral_amount = Decimal('1000')
    first_referral_referrer_bonus = Decimal('100')
    first_referral_referee_bonus = Decimal('10')
    referrer_percentage = Decimal('1')
    referrer_next_duration = -1
    referrer_percentage_2 = 0
    referee_percentage = Decimal('10')
    referee_next_duration = -1
    referee_percentage_2 = 0
