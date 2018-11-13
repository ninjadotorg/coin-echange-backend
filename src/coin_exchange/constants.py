from decimal import Decimal

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

TRACKING_ADDRESS_STATUS = Choices(
    ('created', 'Created'),
    ('has_order', 'Has Order'),
    ('has_payment', 'Has Payment'),
    ('completed', 'Completed'),
)

FEE_COIN_ORDER_COD = "FEE_COIN_ORDER_COD"
FEE_COIN_ORDER_BANK = "FEE_COIN_ORDER_BANK"
FEE_COIN_SELLING_ORDER_BANK = "FEE_COIN_SELLING_ORDER_BANK"

MIN_ETH_AMOUNT = Decimal('0.01')
MIN_BTC_AMOUNT = Decimal('0.001')

ORDER_EXPIRATION_DURATION = 60 * 15
DIFFERENT_THRESHOLD = Decimal('1')  # 1%
