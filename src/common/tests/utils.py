from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient

from coin_user.factories import ExchangeUserFactory
from common.constants import FIAT_CURRENCY


class AuthenticationUtils(object):
    def __init__(self, client: APIClient, username: str = 'test_username', password: str = 'test_password'):
        self.client = client
        self.username = username
        self.password = password

    def create_user(self, username: str = None):
        user = User.objects.create_user(
            username=username if username else self.username,
            password=self.password,
        )
        return user

    def create_exchange_user(self, username: str = None):
        user = User.objects.create_user(
            username=username if username else self.username,
            password=self.password,
            first_name='First',
            last_name='Last',
        )
        exchange_user = ExchangeUserFactory(user=user, currency=FIAT_CURRENCY.PHP)

        return exchange_user

    def login(self, username: str = None):
        url = reverse('token:token_obtain_pair')
        token_resp = self.client.post(url, data={
            User.USERNAME_FIELD: username if username else self.username,
            'password': self.password,
        })
        token = token_resp.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
