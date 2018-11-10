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

FEE_COIN_ORDER_COD = "FEE_COIN_ORDER_COD"
FEE_COIN_ORDER_BANK = "FEE_COIN_ORDER_BANK"
FEE_COIN_SELLING_ORDER_BANK = "FEE_COIN_SELLING_ORDER_BANK"
