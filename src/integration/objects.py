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
        self.called_check_pending = False

    def check_success(self):
        if not self.called_check_pending:
            raise Exception('Need call check_pending first')
        return self.is_success

    def check_pending(self):
        self.called_check_pending = True
        return self.is_pending


class BTCTransactionResponse(TransactionResponse):
    def check_success(self):
        super(BTCTransactionResponse, self).check_success()
        return True

    def check_pending(self):
        super(BTCTransactionResponse, self).check_pending()
        return self.confirmation < self._get_confirmation_range()

    def _get_confirmation_range(self) -> int:
        if self.amount < Decimal('5'):
            return 1
        if self.amount < Decimal('10'):
            return 3
        return 6


class ETHTransactionResponse(TransactionResponse):
    def check_success(self):
        super(ETHTransactionResponse, self).check_success()
        return self.is_success

    def check_pending(self):
        super(ETHTransactionResponse, self).check_pending()
        return self.is_pending
