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
