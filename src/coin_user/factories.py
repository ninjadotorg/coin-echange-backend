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
    country = factory.Iterator([COUNTRY.VN, COUNTRY.HK])
    language = factory.Iterator([LANGUAGE.vi, LANGUAGE.en_us])
