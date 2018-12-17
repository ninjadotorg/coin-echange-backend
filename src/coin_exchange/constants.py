from decimal import Decimal

from model_utils import Choices


ORDER_STATUS = Choices(
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('fiat_transferring', 'Fiat Transferring'),
    ('transferring', 'Transferring'),
    ('transferred', 'Transferred'),
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

ORDER_USER_PAYMENT_TYPE = Choices(
    ('bank', 'Bank'),
    ('tng', 'TNG'),
    ('payoneer', 'Payoneer'),
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

TRACKING_TRANSACTION_STATUS = Choices(
    ('pending', 'Pending'),
    ('success', 'Success'),
    ('failed', 'Failed'),
)

TRACKING_TRANSACTION_DIRECTION = Choices(
    ('transfer_in', 'Transfer In'),
    ('transfer_out', 'Transfer Out'),
)

REFERRAL_STATUS = Choices(
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('paid', 'Paid'),
    ('rejected', 'Rejected'),
)

PROMOTION = Choices(
    ('first_click', 'First Click'),
    ('referrer', 'Referrer'),
    ('referee', 'Referee'),
)

CRYPTO_FUND_TYPE = Choices(
    ('in_fund', 'In Fund'),
    ('out_fund', 'Out Fund'),
    ('storage_fund', 'Storage Fund'),
)

CRYPTO_FUND_ACTION = Choices(
    ('update', 'Update'),
    ('transfer', 'Transfer'),
    ('convert', 'Convert'),
)

CRYPTO_FUND_ACTION_STATUS = Choices(
    ('transferring', 'Transferring'),
    ('transferred', 'Transferred'),
    ('converting', 'Converting'),
    ('converted', 'Converted'),
)

FEE_COIN_ORDER_COD = "FEE_COIN_ORDER_COD"
FEE_COIN_ORDER_BANK = "FEE_COIN_ORDER_BANK"
FEE_COIN_SELLING_ORDER_BANK = "FEE_COIN_SELLING_ORDER_BANK"
FEE_COIN_SELLING_ORDER_COD = "FEE_COIN_SELLING_ORDER_COD"
REFERRER_BONUS = "REFERER_BONUS"
REFEREE_BONUS = "REFEREE_BONUS"

CONFIG_USER_LIMIT = "{}_USER_LIMIT_{}"

MIN_ETH_AMOUNT = Decimal('0.1')
MIN_BTC_AMOUNT = Decimal('0.01')

ORDER_EXPIRATION_DURATION = 60 * 15
DIFFERENT_THRESHOLD = Decimal('1')  # 1%
REF_CODE_LENGTH = 6
