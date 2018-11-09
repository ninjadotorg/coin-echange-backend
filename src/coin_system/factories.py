import factory


class ConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_system.Config'


class FeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_system.Fee'


class BankFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_system.Bank'


class CountryCurrencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_system.CountryCurrency'


class PopularPlaceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_system.PopularPlace'


class CountryDefaultConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_system.CountryDefaultConfig'
