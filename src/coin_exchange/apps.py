from django.apps import AppConfig


class CoinExchangeAppConfig(AppConfig):
    name = "coin_exchange"
    verbose_name = '1. Exchange'

    def ready(self):
        from . import signals  # noqa
        pass
