import factory

from coin_user.factories import ExchangeUserFactory


class PoolFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_exchange.Pool'


class UserLimitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_exchange.UserLimit'

    user = factory.SubFactory(ExchangeUserFactory)
