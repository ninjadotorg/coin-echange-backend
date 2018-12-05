from decimal import Decimal

import requests
from common.decorators import raise_api_exception
from integration.exceptions import ExternalAPIException


class Client(object):
    def __init__(self):
        self.url = 'https://api.coincap.io/v2'

    def get_rate(self, symbol: str):
        resp = requests.get('{}/rates/{}'.format(self.url, symbol))
        if resp.status_code == 200:
            return resp.json()

        raise Exception('API issue HTTP Status {} Response {}'.format(resp.status_code, resp.content))


client = Client()


@raise_api_exception(ExternalAPIException)
def get_rate(symbol: str):
    rate = client.get_rate(symbol)['data']
    result = {'symbol': rate['symbol'], 'rateUsd': Decimal(str(rate['rateUsd']))}

    return result
