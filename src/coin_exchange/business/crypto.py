from decimal import Decimal

from django.conf import settings
from django.db.models import Q

from coin_exchange.constants import TRACKING_ADDRESS_STATUS
from coin_exchange.models import TrackingAddress, Order, TrackingTransaction
from coin_user.models import ExchangeUser
from common.constants import CURRENCY
from common.provider_data import BitstampTxData
from integration import coinbase, bitpay, etherscan, bitstamp
from integration.objects import AddressResponse, TransactionResponse


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
            tx_id = bitstamp.send_transaction(address, currency, amount)
            # Get transaction in 1 minutes to find this one
            list_tx = bitstamp.list_withdrawal_requests(1*60)
            for tx in list_tx:
                if tx['id'] == tx_id:
                    tx_hash = tx['transaction_id']
                    break

            provider_data['tx_id'] = tx_id

        return tx_hash, BitstampTxData(provider_data).to_json()

    @staticmethod
    def create_tracking_tx(order: Order, direction: str):
        TrackingTransaction.objects.create(
            order=order,
            tx_hash=order.tx_hash,
            currency=order.currency,
            direction=direction
        )

    @staticmethod
    def create_tracking_address(order: Order):
        TrackingAddress.objects.create(
            user=order.user,
            order=order,
            currency=order.currency,
            status=TRACKING_ADDRESS_STATUS.has_order
        )


class TrackingManagement(object):
    @staticmethod
    def load_tracking_address():
        pass

    @staticmethod
    def load_tracking_transaction():
        pass

    @staticmethod
    def track_system_address(pk: int):
        pass

    @staticmethod
    def track_system_transaction(pk: int):
        pass

    @staticmethod
    def track_network_address(address: str, currency: str) -> AddressResponse:
        if settings.TEST:
            return AddressResponse(address, Decimal('0'), tx_hashes=['TestTxHash'])

        if currency == CURRENCY.ETH:
            return etherscan.get_address(address)
        if currency == CURRENCY.BTC:
            return bitpay.get_btc_address(address)

    @staticmethod
    def track_network_transaction(tx_hash: str, currency: str):
        if settings.TEST:
            return TransactionResponse(tx_hash, Decimal('0'), is_pending=True, is_success=True)

        if currency == CURRENCY.ETH:
            return etherscan.get_transaction(tx_hash)
        if currency == CURRENCY.BTC:
            return bitpay.get_btc_transaction(tx_hash)

    @staticmethod
    def remove_tracking(order: Order):
        TrackingTransaction.objects.filter(Q(order=order) | Q(address=order.order_address)).delete()
        TrackingAddress.objects.filter(order=order).delete()
