import logging

import simplejson

import requests
from django.conf import settings
from requests import Timeout

from coin_user.models import ExchangeUser
from common.business import get_now


class UserVerificationManagement(object):
    @staticmethod
    def send_user_verification_request(user: ExchangeUser):
        if settings.UNIT_TEST:
            return

        url = settings.NOTIFICATION_API + '/user-verification-notification/'
        try:
            requests.post(url, json={
                'level': user.verification_level,
                'id': user.id,
                'name': user.name,
            }, headers={'Content-type': 'application/json'}, timeout=200)
        except Timeout:
            pass
        except Exception as ex:
            logging.error(ex)


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


class UserManagement(object):
    @staticmethod
    def update_first_purchase(user: ExchangeUser):
        if not user.first_purchase:
            user.first_purchase = get_now()
            user.save(update_fields=['first_purchase'])
