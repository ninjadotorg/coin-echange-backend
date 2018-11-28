from model_utils import Choices

FEE_TYPE = Choices(
    ('fixed', 'Fixed'),
    ('percentage', 'Percentage'),
)

CACHE_KEY_CONFIG = 'system_config.{}'
CACHE_KEY_FEE = 'system_fee.{}'
CACHE_KEY_COUNTRY_DEFAULT = 'system_country_default.{}'
CACHE_KEY_SYSTEM_NOTIFICATION = 'system_notification'
CACHE_KEY_SYSTEM_REMINDER = 'system_reminder'
CACHE_KEY_BONUS = 'system_bonus.{}'
