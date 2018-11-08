import logging

from decimal import Decimal

from bitstamp import client
from bitstamp.client import BitstampError
from django.conf import settings

from common.decorators import raise_api_exception
from integration.exceptions import ExternalAPIException

public_client = client.Public()
trading_client = client.Trading(settings.BITSTAMP['CUSTOMER_ID'],
                                settings.BITSTAMP['API_KEY'],
                                settings.BITSTAMP['API_SECRET'])


@raise_api_exception(ExternalAPIException)
def get_buy_price(currency: str) -> str:
    return public_client.ticker(base=currency.lower())['ask']


@raise_api_exception(ExternalAPIException)
def get_sell_price(currency: str) -> str:
    return public_client.ticker(base=currency.lower())['bid']


@raise_api_exception(ExternalAPIException)
def send_transaction(address: str, currency: str, amount: Decimal):
    resp = 0

    if currency == 'BTC':
        resp = trading_client.bitcoin_withdrawal(amount.__str__(), address)
    elif currency == 'ETH':
        resp = trading_client.ethereum_withdrawal(amount.__str__(), address)

    return resp
