from decimal import Decimal

import requests
from django.conf import settings

from common.decorators import raise_api_exception
from integration.exceptions import ExternalAPIException


class Client(object):
    def __init__(self, api_key: str):
        self.url = 'https://openexchangerates.org/api'
        self.api_key = api_key

    def get_rates(self):
        resp = requests.get('{}/latest.json?app_id={}'.format(self.url, self.api_key))
        if resp.status_code == 200:
            return resp.json()

        raise Exception('API issue HTTP Status {} Response {}'.format(resp.status_code, resp.content))


client = Client(settings.OPENEXCHANGERATES['API_KEY'])


@raise_api_exception(ExternalAPIException)
def get_rates():
    rates = client.get_rates()['rates']
    result = [{'currency': key, 'value': Decimal(str(value))} for key, value in rates.items()]

    return result
