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
