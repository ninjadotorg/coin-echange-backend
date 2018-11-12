from decimal import Decimal
from unittest.mock import MagicMock

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from coin_exchange.constants import FEE_COIN_ORDER_BANK, FEE_COIN_ORDER_COD, FEE_COIN_SELLING_ORDER_BANK
from coin_exchange.factories import PoolFactory, UserLimitFactory
from coin_system.constants import FEE_TYPE
from coin_system.factories import FeeFactory
from coin_user.factories import ExchangeUserFactory
from common.business import PriceManagement, RateManagement, CryptoPrice
from common.constants import CURRENCY, FIAT_CURRENCY, DIRECTION
from common.tests.utils import AuthenticationUtils


class BuyingQuoteTests(APITestCase):
    def setUp(self):
        self.auth_utils = AuthenticationUtils(self.client)

        PriceManagement.get_cache_price = MagicMock(return_value=CryptoPrice(
            CURRENCY.ETH,
            Decimal('100'),
            Decimal('100'),
        ))
        RateManagement.get_cache_rate = MagicMock(return_value=Decimal('23000'))

        FeeFactory(key=FEE_COIN_ORDER_BANK, value=Decimal('1'), fee_type=FEE_TYPE.percentage)
        FeeFactory(key=FEE_COIN_ORDER_COD, value=Decimal('10'), fee_type=FEE_TYPE.percentage)

        PoolFactory(currency=CURRENCY.ETH, direction=DIRECTION.buy, usage=1, limit=2)

        user = self.auth_utils.create_user()
        exchange_user = ExchangeUserFactory(user=user)

        UserLimitFactory(fiat_currency=FIAT_CURRENCY.VND, direction=DIRECTION.buy, usage=2300000, limit=3000000,
                         user=exchange_user)

    def test_invalid(self):
        url = reverse('exchange:quote-detail')
        response = self.client.get(url, data={
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crypto_rate(self):
        url = reverse('exchange:quote-detail')
        response = self.client.get(url, data={
            'amount': '1',
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.VND,
        }, format='json')

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['fiat_amount'], Decimal(101), '100 added 1%')
        self.assertEqual(data['fiat_amount_cod'], Decimal(110), '100 added 10%')
        self.assertEqual(data['fiat_local_amount'], Decimal(2323000), '100 added 1% * 23000')
        self.assertEqual(data['fiat_local_amount_cod'], Decimal(2530000), '100 added 10% * 23000')

    def test_check_pool_limit_success(self):
        url = reverse('exchange:quote-detail')
        response = self.client.get(url, data={
            'amount': '1',
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.VND,
            'check': True,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_pool_over_limit(self):
        url = reverse('exchange:quote-detail')
        response = self.client.get(url, data={
            'amount': '2',
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.VND,
            'check': True,
        }, format='json')

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['code'], 'coin_over_limit')

    def test_check_user_limit_success(self):
        self.auth_utils.login()

        url = reverse('exchange:quote-detail')

        response = self.client.get(url, data={
            'amount': '0.1',
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.VND,
            'user_check': True,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_user_over_limit(self):
        self.auth_utils.login()
        url = reverse('exchange:quote-detail')

        response = self.client.get(url, data={
            'amount': '1',
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.VND,
            'user_check': True,
        }, format='json')

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['code'], 'coin_user_over_limit')

    def test_check_user_without_limit_setup(self):
        url = reverse('exchange:quote-detail')
        username = 'another_username'
        self.auth_utils.create_user(username)
        self.auth_utils.login(username)

        response = self.client.get(url, data={
            'amount': '1',
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.VND,
            'user_check': True,
        }, format='json')

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['code'], 'invalid_data')

    def test_check_user_without_login(self):
        url = reverse('exchange:quote-detail')

        response = self.client.get(url, data={
            'amount': '1',
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.VND,
            'user_check': True,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SellingQuoteTests(APITestCase):
    def setUp(self):
        self.auth_utils = AuthenticationUtils(self.client)

        PriceManagement.get_cache_price = MagicMock(return_value=CryptoPrice(
            CURRENCY.ETH,
            Decimal('100'),
            Decimal('100'),
        ))
        RateManagement.get_cache_rate = MagicMock(return_value=Decimal('23000'))

        FeeFactory(key=FEE_COIN_SELLING_ORDER_BANK, value=Decimal('1'), fee_type=FEE_TYPE.percentage)
        PoolFactory(currency=CURRENCY.ETH, direction=DIRECTION.sell, usage=1, limit=2)

        user = self.auth_utils.create_user()
        exchange_user = ExchangeUserFactory(user=user)
        UserLimitFactory(fiat_currency=FIAT_CURRENCY.VND, direction=DIRECTION.sell, usage=2300000, limit=3000000,
                         user=exchange_user)

    def test_invalid(self):
        url = reverse('exchange:quote-detail')
        response = self.client.get(url, data={
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crypto_rate(self):
        url = reverse('exchange:quote-detail')
        response = self.client.get(url, data={
            'amount': '1',
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.VND,
            'direction': DIRECTION.sell
        }, format='json')

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['fiat_amount'], Decimal(101), '100 added 1%')
        self.assertEqual(data['fiat_amount_cod'], 0, 'Not support')
        self.assertEqual(data['fiat_local_amount'], Decimal(2323000), '100 added 1% * 23000')
        self.assertEqual(data['fiat_local_amount_cod'], 0, 'Not support')

    def test_check_pool_limit_success(self):
        url = reverse('exchange:quote-detail')
        response = self.client.get(url, data={
            'amount': '1',
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.VND,
            'check': True,
            'direction': DIRECTION.sell
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_pool_over_limit(self):
        url = reverse('exchange:quote-detail')
        response = self.client.get(url, data={
            'amount': '2',
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.VND,
            'check': True,
            'direction': DIRECTION.sell
        }, format='json')

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['code'], 'coin_over_limit')

    def test_check_user_limit_success(self):
        self.auth_utils.login()
        url = reverse('exchange:quote-detail')

        response = self.client.get(url, data={
            'amount': '0.1',
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.VND,
            'user_check': True,
            'direction': DIRECTION.sell
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_user_over_limit(self):
        self.auth_utils.login()
        url = reverse('exchange:quote-detail')

        response = self.client.get(url, data={
            'amount': '1',
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.VND,
            'user_check': True,
            'direction': DIRECTION.sell
        }, format='json')

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['code'], 'coin_user_over_limit')

    def test_check_user_without_limit_setup(self):
        url = reverse('exchange:quote-detail')
        username = 'another_username'
        self.auth_utils.create_user(username)
        self.auth_utils.login(username)

        response = self.client.get(url, data={
            'amount': '1',
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.VND,
            'user_check': True,
            'direction': DIRECTION.sell
        }, format='json')

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['code'], 'invalid_data')

    def test_check_user_without_login(self):
        url = reverse('exchange:quote-detail')

        response = self.client.get(url, data={
            'amount': '1',
            'currency': CURRENCY.ETH,
            'fiat_currency': FIAT_CURRENCY.VND,
            'user_check': True,
            'direction': DIRECTION.sell
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BuyingQuoteReverseTests(APITestCase):
    def setUp(self):
        PriceManagement.get_cache_price = MagicMock(return_value=CryptoPrice(
            CURRENCY.ETH,
            Decimal('100'),
            Decimal('100'),
        ))
        RateManagement.get_cache_rate = MagicMock(return_value=Decimal('23000'))

        FeeFactory(key=FEE_COIN_ORDER_BANK, value=Decimal('1'), fee_type=FEE_TYPE.percentage)
        FeeFactory(key=FEE_COIN_ORDER_COD, value=Decimal('10'), fee_type=FEE_TYPE.percentage)

        PoolFactory(currency=CURRENCY.ETH, direction=DIRECTION.buy, usage=1, limit=2)

        self.password = 'test_password'
        self.username = 'test_username'
        user = self._create_user(self.username)

        exchange_user = ExchangeUserFactory(user=user)
        UserLimitFactory(fiat_currency=FIAT_CURRENCY.VND, direction=DIRECTION.buy, usage=2300000, limit=3000000,
                         user=exchange_user)

    def test_invalid(self):
        url = reverse('exchange:quote-reverse-detail')
        response = self.client.get(url, data={
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crypto_rate(self):
        url = reverse('exchange:quote-reverse-detail')
        response = self.client.get(url, data={
            'currency': CURRENCY.ETH,
            'fiat_amount': '2323000',
            'fiat_currency': FIAT_CURRENCY.VND,
        }, format='json')

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['amount'], Decimal(1))

    def test_check_pool_limit_success(self):
        url = reverse('exchange:quote-reverse-detail')
        response = self.client.get(url, data={
            'currency': CURRENCY.ETH,
            'fiat_amount': '2323000',
            'fiat_currency': FIAT_CURRENCY.VND,
            'check': True,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_pool_over_limit(self):
        url = reverse('exchange:quote-reverse-detail')
        response = self.client.get(url, data={
            'currency': CURRENCY.ETH,
            'fiat_amount': '4646000',  # 2 ETH
            'fiat_currency': FIAT_CURRENCY.VND,
            'check': True,
        }, format='json')

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['code'], 'coin_over_limit')

    def test_check_user_limit_success(self):
        self._login(self.username)
        url = reverse('exchange:quote-reverse-detail')

        response = self.client.get(url, data={
            'currency': CURRENCY.ETH,
            'fiat_amount': '232300',  # 0.1 ETH
            'fiat_currency': FIAT_CURRENCY.VND,
            'user_check': True,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_user_over_limit(self):
        self._login(self.username)
        url = reverse('exchange:quote-reverse-detail')

        response = self.client.get(url, data={
            'currency': CURRENCY.ETH,
            'fiat_amount': '2323000',
            'fiat_currency': FIAT_CURRENCY.VND,
            'user_check': True,
        }, format='json')

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['code'], 'coin_user_over_limit')

    def test_check_user_without_limit_setup(self):
        url = reverse('exchange:quote-reverse-detail')
        username = 'another_username'
        self._create_user(username)
        self._login(username)

        response = self.client.get(url, data={
            'currency': CURRENCY.ETH,
            'fiat_amount': '2323000',
            'fiat_currency': FIAT_CURRENCY.VND,
            'user_check': True,
        }, format='json')

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['code'], 'invalid_data')

    def test_check_user_without_login(self):
        url = reverse('exchange:quote-reverse-detail')

        response = self.client.get(url, data={
            'currency': CURRENCY.ETH,
            'fiat_amount': '2323000',
            'fiat_currency': FIAT_CURRENCY.VND,
            'user_check': True,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _create_user(self, username):
        user = User.objects.create_user(
            username=username,
            password=self.password,
        )
        return user

    def _login(self, username):
        url = reverse('token:token_obtain_pair')
        token_resp = self.client.post(url, data={
            User.USERNAME_FIELD: username,
            'password': self.password,
        })
        token = token_resp.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)


class SellingQuoteReverseTests(APITestCase):
    def setUp(self):
        PriceManagement.get_cache_price = MagicMock(return_value=CryptoPrice(
            CURRENCY.ETH,
            Decimal('100'),
            Decimal('100'),
        ))
        RateManagement.get_cache_rate = MagicMock(return_value=Decimal('23000'))

        FeeFactory(key=FEE_COIN_SELLING_ORDER_BANK, value=Decimal('1'), fee_type=FEE_TYPE.percentage)
        PoolFactory(currency=CURRENCY.ETH, direction=DIRECTION.sell, usage=1, limit=2)

        self.password = 'test_password'
        self.username = 'test_username'
        user = self._create_user(self.username)

        exchange_user = ExchangeUserFactory(user=user)
        UserLimitFactory(fiat_currency=FIAT_CURRENCY.VND, direction=DIRECTION.sell, usage=2300000, limit=3000000,
                         user=exchange_user)

    def test_invalid(self):
        url = reverse('exchange:quote-reverse-detail')
        response = self.client.get(url, data={
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crypto_rate(self):
        url = reverse('exchange:quote-reverse-detail')
        response = self.client.get(url, data={
            'currency': CURRENCY.ETH,
            'fiat_amount': '2323000',
            'fiat_currency': FIAT_CURRENCY.VND,
            'direction': DIRECTION.sell
        }, format='json')

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['fiat_amount'], Decimal(101), '100 added 1%')
        self.assertEqual(data['fiat_local_amount'], Decimal(2323000), '100 added 1% * 23000')

    def test_check_pool_limit_success(self):
        url = reverse('exchange:quote-reverse-detail')
        response = self.client.get(url, data={
            'currency': CURRENCY.ETH,
            'fiat_amount': '2323000',
            'fiat_currency': FIAT_CURRENCY.VND,
            'check': True,
            'direction': DIRECTION.sell
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_pool_over_limit(self):
        url = reverse('exchange:quote-reverse-detail')
        response = self.client.get(url, data={
            'currency': CURRENCY.ETH,
            'fiat_amount': '4646000',
            'fiat_currency': FIAT_CURRENCY.VND,
            'check': True,
            'direction': DIRECTION.sell
        }, format='json')

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['code'], 'coin_over_limit')

    def test_check_user_limit_success(self):
        self._login(self.username)
        url = reverse('exchange:quote-reverse-detail')

        response = self.client.get(url, data={
            'currency': CURRENCY.ETH,
            'fiat_amount': '232300',
            'fiat_currency': FIAT_CURRENCY.VND,
            'user_check': True,
            'direction': DIRECTION.sell
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_user_over_limit(self):
        self._login(self.username)
        url = reverse('exchange:quote-reverse-detail')

        response = self.client.get(url, data={
            'currency': CURRENCY.ETH,
            'fiat_amount': '2323000',
            'fiat_currency': FIAT_CURRENCY.VND,
            'user_check': True,
            'direction': DIRECTION.sell
        }, format='json')

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['code'], 'coin_user_over_limit')

    def test_check_user_without_limit_setup(self):
        url = reverse('exchange:quote-reverse-detail')
        username = 'another_username'
        self._create_user(username)
        self._login(username)

        response = self.client.get(url, data={
            'currency': CURRENCY.ETH,
            'fiat_amount': '2323000',
            'fiat_currency': FIAT_CURRENCY.VND,
            'user_check': True,
            'direction': DIRECTION.sell
        }, format='json')

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['code'], 'invalid_data')

    def test_check_user_without_login(self):
        url = reverse('exchange:quote-reverse-detail')

        response = self.client.get(url, data={
            'currency': CURRENCY.ETH,
            'fiat_amount': '2323000',
            'fiat_currency': FIAT_CURRENCY.VND,
            'user_check': True,
            'direction': DIRECTION.sell
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _create_user(self, username):
        user = User.objects.create_user(
            username=username,
            password=self.password,
        )
        return user

    def _login(self, username):
        url = reverse('token:token_obtain_pair')
        token_resp = self.client.post(url, data={
            User.USERNAME_FIELD: username,
            'password': self.password,
        })
        token = token_resp.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
