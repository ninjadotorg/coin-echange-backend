import factory
from django.contrib.auth.models import User


class DjangoUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User


class ExchangeUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_user.ExchangeUser'

    user = factory.SubFactory(DjangoUserFactory)
