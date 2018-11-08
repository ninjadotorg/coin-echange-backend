from decimal import Decimal

from django.core.cache import cache

from coin_exchange.constants import CACHE_KEY_CRYPTO_RATE_CURRENCY_BY_EXCHANGE, EXCHANGE_SITE, CACHE_KEY_CURRENCY_RATE
from integration.bitstamp import get_buy_price, get_sell_price
from integration.openexchangerates import get_rates


class CoinPrice(object):
    def __init__(self, currency: str, buy: Decimal, sell: Decimal):
        self.currency = currency
        self.buy = buy
        self.sell = sell


def save_cache_price(currency: str):
    buy_price = get_buy_price(currency)
    sell_price = get_sell_price(currency)

    coin_price = CoinPrice(currency, Decimal(buy_price), Decimal(sell_price))

    cache.set(CACHE_KEY_CRYPTO_RATE_CURRENCY_BY_EXCHANGE.format(currency, EXCHANGE_SITE.coinbase),
              coin_price, timeout=None)


def get_cache_price(currency: str):
    return cache.get(CACHE_KEY_CRYPTO_RATE_CURRENCY_BY_EXCHANGE.format(currency, EXCHANGE_SITE.coinbase))


def save_rates():
    rates = get_rates()
    for rate in rates:
        cache.set(CACHE_KEY_CURRENCY_RATE.format(rate['currency']), rate['value'],
                  timeout=None)


def get_cache_rate(currency: str) -> Decimal:
    return cache.get(CACHE_KEY_CURRENCY_RATE.format(currency))
