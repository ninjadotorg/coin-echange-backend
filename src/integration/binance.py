from decimal import Decimal

from binance.client import Client
from django.conf import settings

from common.business import get_now
from common.decorators import raise_api_exception
from integration.exceptions import ExternalAPIException

client = Client(settings.BINANCE['API_KEY'], settings.BINANCE['SECRET_KEY'])


@raise_api_exception(ExternalAPIException)
def get_address(currency: str) -> str:
    return client.get_deposit_address(asset=currency)


@raise_api_exception(ExternalAPIException)
def send_transaction(address: str, currency: str, amount: Decimal):
    result = client.withdraw(
        asset=currency,
        address=address,
        amount=amount)

    if result['status'] > 0:
        raise Exception('Binance: Something wrong when transfer')

    return result


@raise_api_exception(ExternalAPIException)
def send_sell_order(symbol: str, amount: Decimal, test=False):
    return send_order(symbol, amount, 'SELL', test=test)


@raise_api_exception(ExternalAPIException)
def send_buy_order(symbol: str, amount: Decimal, test=False):
    return send_order(symbol, amount, 'BUY', test=test)


def send_order(symbol: str, amount: Decimal, side: str, test=False):
    data = {
        'symbol': symbol,
        'side': side,
        'type': 'MARKET',
        'quantity': amount,
        'timestamp': get_now().timestamp(),
        'newOrderRespType': 'RESULT',
    }

    if test:
        result = client.create_test_order(**data)
        return result

    result = client.create_order(**data)
    return result


@raise_api_exception(ExternalAPIException)
def get_account():
    return client.get_account(timestamp=get_now().timestamp())
