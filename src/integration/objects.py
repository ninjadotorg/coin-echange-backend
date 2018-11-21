from decimal import Decimal


class AddressResponse(object):
    def __init__(self, address, balance: Decimal, tx_hashes=None, unconfirmed_balance=None, unconfirmed_tx=None):
        self.address = address
        self.balance = balance
        self.tx_hashes = tx_hashes
        self.unconfirmed_balance = unconfirmed_balance
        self.unconfirmed_tx = unconfirmed_tx


class TransactionResponse(object):
    def __init__(self, tx_hash, amount: Decimal, confirmation=None, is_pending=True, is_success=False):
        self.tx_hash = tx_hash
        self.amount = amount
        self.confirmation = confirmation
        self.is_pending = is_pending
        self.is_success = is_success
