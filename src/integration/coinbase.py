from coinbase.wallet.client import Client
from django.conf import settings

from common.decorators import raise_api_exception
from integration.exceptions import ExternalAPIException

client = Client(settings.COINBASE['API_KEY'], settings.COINBASE['API_SECRET'])


@raise_api_exception(ExternalAPIException)
def generate_address(currency: str) -> str:
    return client.create_address(settings.COINBASE['ACCOUNTS'][currency]).address


@raise_api_exception(ExternalAPIException)
def get_buy_price(currency: str) -> str:
    return client.get_buy_price(currency_pair='{}-USD'.format(currency)).amount


@raise_api_exception(ExternalAPIException)
def get_sell_price(currency: str) -> str:
    return client.get_sell_price(currency_pair='{}-USD'.format(currency)).amount
