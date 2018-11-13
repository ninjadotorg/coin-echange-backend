import random
import string
from decimal import Decimal
from typing import List

import coinaddr
from django.core.cache import cache
from django.utils import timezone

from common.constants import CACHE_KEY_CRYPTO_RATE_CURRENCY_BY_EXCHANGE, CACHE_KEY_CURRENCY_RATE, EXCHANGE_SITE
from common.exceptions import InvalidDataException
from integration.bitstamp import get_buy_price, get_sell_price
from integration.openexchangerates import get_rates


class CryptoPrice(object):
    def __init__(self, currency: str, buy: Decimal, sell: Decimal):
        self.currency = currency
        self.buy = buy
        self.sell = sell


class PriceManagement(object):
    @staticmethod
    def save_cache_price(currency: str) -> CryptoPrice:
        buy_price = get_buy_price(currency)
        sell_price = get_sell_price(currency)

        coin_price = CryptoPrice(currency, Decimal(buy_price), Decimal(sell_price))

        cache.set(CACHE_KEY_CRYPTO_RATE_CURRENCY_BY_EXCHANGE.format(currency, EXCHANGE_SITE.coinbase),
                  coin_price, timeout=None)

        return coin_price

    @staticmethod
    def get_cache_price(currency: str) -> CryptoPrice:
        data = cache.get(CACHE_KEY_CRYPTO_RATE_CURRENCY_BY_EXCHANGE.format(currency, EXCHANGE_SITE.coinbase))
        if not data:
            raise InvalidDataException
        return data


class RateManagement(object):
    @staticmethod
    def save_rates():
        rates = get_rates()
        for rate in rates:
            cache.set(CACHE_KEY_CURRENCY_RATE.format(rate['currency']), rate['value'],
                      timeout=None)

    @staticmethod
    def get_cache_rate(currency: str) -> Decimal:
        data = cache.get(CACHE_KEY_CURRENCY_RATE.format(currency))
        if not data:
            raise InvalidDataException
        return data

    @staticmethod
    def convert_to_local_currency(amount: Decimal, currency: str) -> Decimal:
        rate = RateManagement.get_cache_rate(currency)
        return rate * amount

    @staticmethod
    def convert_from_local_currency(amount: Decimal, currency: str) -> Decimal:
        rate = RateManagement.get_cache_rate(currency)
        return amount / rate


def view_serializer_fields(fields: List[str], serializer_data: dict) -> dict:
    data = {key: serializer_data[key] for key in fields}
    return data


def validate_crypto_address(currency: str, address: str) -> bool:
    result = coinaddr.validate(currency.lower(), address)
    return result.valid


def get_now():
    now = timezone.now()
    # if not timezone.is_naive(now):
    #     now = timezone.make_naive(now, timezone.utc)

    return now


def generate_random_code(n: int):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))
