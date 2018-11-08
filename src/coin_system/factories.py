import factory


class ConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_system.Config'


class FeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coin_system.Fee'
