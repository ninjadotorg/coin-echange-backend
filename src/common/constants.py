from model_utils import Choices

VALUE_TYPE = Choices(
    ('int', 'Number'),
    ('decimal', 'Currency'),
    ('string', 'Text'),
)

LANGUAGE = Choices(
    ('en-US', 'English'),
    ('vi', 'Vietnamese'),
)

COUNTRY = Choices(
    ('HK', 'Hong Kong'),
    ('VN', 'Viet Nam'),
)

DIRECTION = Choices(
    ('buy', 'Buy'),
    ('sell', 'Sell'),
)

FIAT_CURRENCY = Choices(
    ('VND', 'VND'),
    ('HKD', 'HKD'),
    ('USD', 'USD'),
)

CURRENCY = Choices(
    ('ETH', 'ETH'),
    ('BTC', 'BTC'),
)

SUPPORT_CURRENCIES = [
    CURRENCY.ETH,
    CURRENCY.BTC,
]

SUPPORT_FIAT_CURRENCIES = [
    FIAT_CURRENCY.HKD,
    FIAT_CURRENCY.USD,
    FIAT_CURRENCY.VND,
]

EXCHANGE_SITE = Choices(
    ('coinbase', 'Coinbase'),
    ('bitstamp', 'BitStamp'),
)

CACHE_KEY_CRYPTO_RATE_CURRENCY_BY_EXCHANGE = 'crypto_rates.{}_{}'
CACHE_KEY_CURRENCY_RATE = 'currency_rates.{}'
