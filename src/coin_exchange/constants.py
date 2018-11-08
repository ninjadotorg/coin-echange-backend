from model_utils import Choices


ORDER_STATUS = Choices(
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('fiat_transferring', 'Fiat Transferring'),
    ('transferring', 'Transferring'),
    ('success', 'Success'),
    ('transfer_failed', 'Transfer Failed'),
    ('cancelled', 'Cancelled'),
    ('rejected', 'Rejected'),
    ('expired', 'Expired'),
)

ORDER_TYPE = Choices(
    ('bank', 'Bank'),
    ('cod', 'COD')
)

PAYMENT_STATUS = Choices(
    ('matched', 'Matched'),
    ('under', 'Under'),
    ('over', 'Over'),
)

CACHE_KEY_CRYPTO_RATE_CURRENCY_BY_EXCHANGE = 'crypto_rates.{}_{}'
CACHE_KEY_CURRENCY_RATE = 'currency_rates.{}'
