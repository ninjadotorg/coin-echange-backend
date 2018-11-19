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
    ('successful_email_verification', 'Successful email verification'),
    ('successful_phone_verification', 'Successful phone verification'),
    ('successful_id_verification', 'Successful ID verification'),
    ('failed_id_verification', 'Failed ID verification'),
    ('successful_selfie_verification', 'Successful selfie verification'),
    ('gift_promotion', 'Gift promotion'),
    ('coin_price', 'Coin price'),
    ('successful_buying', 'Successful buying'),
    ('successful_selling', 'Successful selling'),
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
