from coin_exchange.constants import TRACKING_ADDRESS_STATUS
from coin_exchange.models import TrackingAddress
from coin_user.models import ExchangeUser
from integration import coinbase


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
