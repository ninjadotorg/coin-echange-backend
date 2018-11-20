from django.apps import AppConfig


class CoinExchangeAppConfig(AppConfig):
    name = "coin_exchange"

    def ready(self):
        from . import signals  # noqa
        pass
