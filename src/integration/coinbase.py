from coinbase.wallet.client import Client
from django.conf import settings

client = Client(settings.COINBASE['API_KEY'], settings.COINBASE['API_SECRET'])


def generate_address(currency: str):
    return client.create_address(settings.COINBASE['ACCOUNTS'][currency])


def get_buy_price(currency: str):
    return client.get_buy_price(currency_pair='{}-USD'.format(currency)).amount


def get_sell_price(currency: str):
    return client.get_sell_price(currency_pair='{}-USD'.format(currency)).amount
