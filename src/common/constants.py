from model_utils import Choices

VALUE_TYPE = Choices(
    ('int', 'Number'),
    ('decimal', 'Currency'),
    ('string', 'Text'),
)

LANGUAGE = Choices(
    ('km', 'km', 'Cambodian'),
    ('en', 'en', 'English'),
    ('id', 'id', 'Indonesian'),
)

COUNTRY = Choices(
    ('KH', 'Cambodia'),
    ('ID', 'Indonesia'),
    ('PH', 'Philippines'),
    ('HK', 'Hong Kong'),
)

# For now user limit only has 1 record
DIRECTION_ALL = 'all'
DIRECTION = Choices(
    ('buy', 'Buy'),
    ('sell', 'Sell'),
)

FIAT_CURRENCY = Choices(
    ('USD', 'USD'),
    ('HKD', 'HKD'),
    ('IDR', 'IDR'),
    ('PHP', 'PHP'),
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
    FIAT_CURRENCY.IDR,
    FIAT_CURRENCY.PHP,
    FIAT_CURRENCY.USD,
    FIAT_CURRENCY.HKD,
]

EXCHANGE_SITE = Choices(
    ('coinbase', 'Coinbase'),
    ('bitstamp', 'BitStamp'),
)

CACHE_KEY_CRYPTO_RATE_CURRENCY_BY_EXCHANGE = 'crypto_rates.{}_{}'
CACHE_KEY_CURRENCY_RATE = 'currency_rates.{}'
CACHE_KEY_FORGOT_PASSWORD = 'forgot_password.{}'
