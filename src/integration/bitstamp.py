from decimal import Decimal

from bitstamp import client
from django.conf import settings

from common.decorators import raise_api_exception
from integration.exceptions import ExternalAPIException


class CustomClientTrading(client.Trading):
    def withdrawal_requests(self, timedelta=86400):
        """
        Returns list of withdrawal requests.

        Each request is represented as a dictionary.

        By default, the last 24 hours (86400 seconds) are returned.
        """
        data = {'timedelta': timedelta}
        return self._post("withdrawal-requests/", return_json=True, version=2, data=data)


public_client = client.Public()
trading_client = CustomClientTrading(settings.BITSTAMP['CUSTOMER_ID'],
                                     settings.BITSTAMP['API_KEY'],
                                     settings.BITSTAMP['API_SECRET'])


@raise_api_exception(ExternalAPIException)
def get_buy_price(currency: str) -> str:
    return public_client.ticker(base=currency.lower())['ask']


@raise_api_exception(ExternalAPIException)
def get_sell_price(currency: str) -> str:
    return public_client.ticker(base=currency.lower())['bid']


@raise_api_exception(ExternalAPIException)
def get_price(currency: str) -> str:
    return public_client.ticker(base=currency.lower())['last']


@raise_api_exception(ExternalAPIException)
def send_transaction(address: str, currency: str, amount: Decimal):
    resp = 0

    if currency == 'BTC':
        resp = trading_client.bitcoin_withdrawal(amount.__str__(), address)
    elif currency == 'ETH':
        resp = trading_client.ethereum_withdrawal(amount.__str__(), address)
    if resp['id'] == 0:
        raise Exception('Bitstamp: Something wrong when transfer')

    return resp


@raise_api_exception(ExternalAPIException)
def list_withdrawal_requests(timedelta=86400):
    return trading_client.withdrawal_requests(timedelta)
