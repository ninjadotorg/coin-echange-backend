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

EXCHANGE_SITE = Choices(
    ('coinbase', 'Coinbase'),
    ('bitstamp', 'BitStamp'),
)
