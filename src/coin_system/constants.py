from model_utils import Choices

FEE_TYPE = Choices(
    ('fixed', 'Fixed'),
    ('percentage', 'Percentage'),
)

SYSTEM_FEE = Choices(
    ('coin_order_bank', 'coin_order_bank'),
    ('coin_order_cod', 'coin_order_bank'),
    ('coin_selling_order_bank', 'coin_selling_order_bank'),
)

EMAIL_PURPOSE = Choices(
    ('email_verification', 'Email verification'),
)

SMS_PURPOSE = Choices(
    ('phone_verification', 'Phone verification'),
)

NOTIFICATION_TARGET = Choices(
    ('user', 'User'),
    ('system', 'System'),
)

CACHE_KEY_CONFIG = 'system_config.{}'
CACHE_KEY_FEE = 'system_fee.{}'
CACHE_KEY_COUNTRY_DEFAULT = 'system_country_default.{}'
