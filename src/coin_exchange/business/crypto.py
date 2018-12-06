from decimal import Decimal

import requests
from django.conf import settings
from django.db import transaction
from django.db.models import Q

from coin_exchange.constants import TRACKING_ADDRESS_STATUS, TRACKING_TRANSACTION_STATUS, \
    TRACKING_TRANSACTION_DIRECTION, ORDER_STATUS, PAYMENT_STATUS
from coin_exchange.models import TrackingAddress, Order, TrackingTransaction, SellingPayment, SellingPaymentDetail
from coin_system.business import round_crypto_currency
from coin_user.models import ExchangeUser
from common.constants import CURRENCY, DIRECTION
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
            tx_id = bitstamp.send_transaction(address, currency, round_crypto_currency(amount))
            # Get transaction in 1 minutes to find this one
            list_tx = bitstamp.list_withdrawal_requests(1 * 60)
            for tx in list_tx:
                if tx['id'] == tx_id['id']:
                    tx_hash = tx.get('transaction_id', '')
                    break

            provider_data['tx_id'] = tx_id['id']

        return tx_hash, BitstampTxData(provider_data).to_json()


class TrackingManagement(object):
    @staticmethod
    @transaction.atomic
    def add_tracking_address_payment(order: Order,
                                     add_payment: bool = True) -> TrackingAddress:
        obj = TrackingAddress.objects.filter(
            user=order.user,
            address=order.address,
            currency=order.currency).first()
        if not obj:
            obj = TrackingAddress.objects.create(
                user=order.user,
                order=order,
                currency=order.currency,
                address=order.address,
                status=TRACKING_ADDRESS_STATUS.has_order
            )
        else:
            obj.status = TRACKING_ADDRESS_STATUS.has_order
            obj.save(update_fields=['status', ])

        if add_payment and order.direction == DIRECTION.sell:
            SellingPayment.objects.create(
                address=order.address,
                order=order,
                amount=0,
                currency=order.currency,
                overspent=0,
                status=PAYMENT_STATUS.under,
            )

        return obj

    @staticmethod
    def create_tracking_transaction(tracking_address: TrackingAddress, tx_hash: str) -> TrackingAddress:
        obj = TrackingTransaction.objects.create(
            tx_hash=tx_hash,
            currency=tracking_address.order.currency,
            order=tracking_address.order,
            direction=TRACKING_TRANSACTION_DIRECTION.transfer_in
            if tracking_address.order.direction == DIRECTION.sell else TRACKING_TRANSACTION_DIRECTION.transfer_out,
            tracking_address=tracking_address,
            to_address=tracking_address.address,
        )

        return obj

    @staticmethod
    def create_tracking_simple_transaction(order: Order):
        TrackingTransaction.objects.create(
            order=order,
            tx_hash=order.tx_hash,
            currency=order.currency,
            direction=TRACKING_TRANSACTION_DIRECTION.transfer_in
            if order.direction == DIRECTION.sell else TRACKING_TRANSACTION_DIRECTION.transfer_out,
        )

    @staticmethod
    def load_tracking_address():
        url = settings.EXCHANGE_API + '/tracking-addresses/{}/'
        for tracking in TrackingAddress.objects.all():
            try:
                # Just don't push too much
                requests.post(url.format(tracking.id), timeout=200)
            except Exception:
                pass

    @staticmethod
    def load_tracking_transaction():
        url = settings.EXCHANGE_API + '/tracking-transactions/{}/'
        for tracking in TrackingTransaction.objects.all():
            try:
                # Just don't push too much
                requests.post(url.format(tracking.id), timeout=200)
            except Exception:
                pass

    @staticmethod
    def track_system_address(pk: int):
        obj = TrackingAddress.objects.get(id=pk)
        network_tracking = TrackingManagement.track_network_address(obj.address, obj.currency)
        tx_hashes = network_tracking.tx_hashes
        tracking_tx_hashes = TrackingTransaction.objects.filter(tracking_address=obj).values_list('tx_hash', flat=True)
        new_tx_hashes = set(tx_hashes) - set(tracking_tx_hashes)

        for tx_hash in new_tx_hashes:
            TrackingManagement.create_tracking_transaction(obj, tx_hash)

    @staticmethod
    @transaction.atomic
    def track_system_transaction(pk: int):
        obj = TrackingTransaction.objects.get(id=pk)
        resp = TrackingManagement.track_network_transaction(obj.tx_hash, obj.currency)
        if resp.check_pending():
            obj.status = TRACKING_TRANSACTION_STATUS.pending
        else:
            if resp.check_success():
                obj.status = TRACKING_TRANSACTION_STATUS.success
            else:
                obj.status = TRACKING_TRANSACTION_STATUS.failed

        if obj.direction == TRACKING_TRANSACTION_DIRECTION.transfer_out:
            order = obj.order
            if order:
                order.status = ORDER_STATUS.success
                order.save(update_fields=['status', 'updated_at'])
        else:
            if obj.status == TRACKING_TRANSACTION_STATUS.success:
                payment = SellingPayment.objects.select_related('order') \
                    .get(address__iexact=obj.tracking_address.address)
                SellingPaymentDetail.objects.create(
                    payment=payment,
                    currency=obj.currency,
                    amount=resp.amount,
                    tx_hash=obj.tx_hash,
                )

    @staticmethod
    def track_network_address(address: str, currency: str) -> AddressResponse:
        if settings.TEST:
            return AddressResponse(address, Decimal('0'), tx_hashes=['TestTxHash'])

        if currency == CURRENCY.ETH:
            return etherscan.get_address(address)
        if currency == CURRENCY.BTC:
            return bitpay.get_btc_address(address)

    @staticmethod
    def track_network_transaction(tx_hash: str, currency: str) -> TransactionResponse:
        if settings.TEST:
            return TransactionResponse(tx_hash, Decimal('0'), is_pending=False, is_success=True)

        if currency == CURRENCY.ETH:
            return etherscan.get_transaction(tx_hash)
        if currency == CURRENCY.BTC:
            return bitpay.get_btc_transaction(tx_hash)

    @staticmethod
    def remove_tracking(order: Order):
        TrackingTransaction.objects.filter(Q(order=order) | Q(to_address__iexact=order.address)).delete()
        TrackingAddress.objects.filter(order=order).delete()

    @staticmethod
    def remove_transaction_tracking(tx_hash: str):
        TrackingTransaction.objects.filter(tx_hash__iexact=tx_hash).delete()
