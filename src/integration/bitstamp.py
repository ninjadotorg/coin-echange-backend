from decimal import Decimal

from bitstamp import client
from bitstamp.client import BitstampError
from django.conf import settings

from integration.exceptions import ExternalAPIException

public_client = client.Public()
trading_client = client.Trading(settings.BITSTAMP['CUSTOMER_ID'],
                                settings.BITSTAMP['API_KEY'],
                                settings.BITSTAMP['API_SECRET'])


def get_buy_price(currency: str):
    return public_client.ticker(base=currency.lower())['ask']


def get_sell_price(currency: str):
    return public_client.ticker(base=currency.lower())['bid']


def send_transaction(address: str, currency: str, amount: Decimal):
    resp = 0
    try:
        if currency == 'BTC':
            resp = trading_client.bitcoin_withdrawal(amount.__str__(), address)
        elif currency == 'ETH':
            resp = trading_client.ethereum_withdrawal(amount.__str__(), address)
    except BitstampError:
        raise ExternalAPIException

    return resp
