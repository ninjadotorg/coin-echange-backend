from unittest import TestCase

from common.business import validate_crypto_address
from common.constants import CURRENCY


class CrypotoAddressValidationTests(TestCase):
    def test_valid_btc(self):
        self.assertEqual(validate_crypto_address(CURRENCY.BTC, '1EyZpaSDUeDmMoNf5Hn5dUQShzY65ecJ8K'), True)

    def test_valid_eth(self):
        self.assertEqual(validate_crypto_address(CURRENCY.ETH, '0x6d86cf435978cb75aecc43d0a4e3a379af7667d8'), True)
