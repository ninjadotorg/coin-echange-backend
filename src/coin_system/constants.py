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

CACHE_KEY_CONFIG = 'system_config.{}'
