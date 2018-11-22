import factory
from django.contrib.auth.models import User

from common.constants import COUNTRY, LANGUAGE


class DjangoUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "Username%03d" % n)


class ExchangeUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_user.ExchangeUser'

    user = factory.SubFactory(DjangoUserFactory)
    country = factory.Iterator([COUNTRY.KH, COUNTRY.ID])
    language = factory.Iterator([LANGUAGE.km, LANGUAGE.en])
    name = factory.Sequence(lambda n: "ExchangeUser%03d" % n)


class ContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_user.Contact'

    user = factory.SubFactory(ExchangeUserFactory)
    name = factory.Sequence(lambda n: "Contact%03d" % n)
