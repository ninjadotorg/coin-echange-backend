from decimal import Decimal

from django.conf import settings

from coin_exchange.constants import TRACKING_ADDRESS_STATUS
from coin_exchange.models import TrackingAddress
from coin_user.models import ExchangeUser
from common.provider_data import BitstampTxData
from integration import coinbase
from integration.bitstamp import send_transaction


class AddressManagement(object):
    @staticmethod
    def generate_address(currency: str) -> str:
        return coinbase.generate_address(currency)

    @staticmethod
    # Return address and a exist flag
    def create_address(user: ExchangeUser, currency: str) -> (str, bool):
        # Re-use unused address
        address_obj = TrackingAddress.objects.filter(user=user, currency=currency,
                                                     status=TRACKING_ADDRESS_STATUS.created).first()
        if address_obj:
            return address_obj.address, True

        # If there is not, generate one
        address = AddressManagement.generate_address(currency)
        # Add to tracking
        TrackingAddress.objects.create(user=user, currency=currency, address=address,
                                       status=TRACKING_ADDRESS_STATUS.created)

        return address, False


class CryptoTransactionManagement(object):
    @staticmethod
    def transfer(address: str, currency: str, amount: Decimal) -> (str, str):
        tx_hash = ''
        provider_data = {}
        if settings.TEST:
            tx_hash = 'ThisIsATestTransactionHash'
            provider_data['tx_id'] = 'TestProviderTransactionId'
        else:
            tx_id = send_transaction(address, currency, amount)
            provider_data['tx_id'] = tx_id

        return tx_hash, BitstampTxData(provider_data).to_json()
