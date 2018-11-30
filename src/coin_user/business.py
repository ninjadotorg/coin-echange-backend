import simplejson

import requests
from django.conf import settings

from coin_user.models import ExchangeUser


class UserVerificationManagement(object):
    @staticmethod
    def send_user_verification_request(user: ExchangeUser):
        url = settings.NOTIFICATION_API + '/user-verification-notification/'
        try:
            requests.post(url, data={
                'level': user.verification_level,
                'id': user.id,
                'name': user.name,
            }, headers={'Content-type': 'application/json'}, timeout=200)
        except Exception:
            pass


class UserWalletManagement(object):
    @staticmethod
    def get_default_address(user: ExchangeUser, currency: str):
        address = ''
        try:
            if user.wallet:
                wallets = simplejson.loads(user.wallet)
                for wallet in wallets:
                    if wallet['name'] == currency:
                        address = wallet['address']
                        if wallet['default']:
                            break
        except Exception:
            pass

        return address
