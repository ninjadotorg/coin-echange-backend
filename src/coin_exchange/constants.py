from model_utils import Choices

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

COUNTRY = Choices(
    ('VN', 'Vietnam'),
    ('HK', 'Hong Kong'),
)
