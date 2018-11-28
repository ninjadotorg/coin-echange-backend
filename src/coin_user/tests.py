from unittest.mock import MagicMock

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from coin_system.factories import CountryDefaultConfigFactory
from coin_user.factories import ContactFactory
from coin_user.views import VerifyEmailView
from common.constants import COUNTRY, FIAT_CURRENCY, LANGUAGE
from common.tests.utils import AuthenticationUtils


class ProfileTests(APITestCase):
    def setUp(self):
        self.auth_utils = AuthenticationUtils(self.client)
        self.user = self.auth_utils.create_exchange_user()
        self.auth_utils.login()

    def test_profile(self):
        url = reverse('user:profile')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_profile(self):
        url = reverse('user:profile')
        updated_name = 'FirstName'
        response = self.client.patch(url, {
            'phone_number': '1234567890',
            'first_name': 'FirstName',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user = User.objects.get(username=self.user.user.username)
        self.assertEqual(user.first_name, updated_name)


class SignUpTests(APITestCase):
    def setUp(self):
        CountryDefaultConfigFactory(country=COUNTRY.PH, currency=FIAT_CURRENCY.PHP, language=LANGUAGE.en)
        VerifyEmailView.send_verification_email = MagicMock(return_value=None)

    def test_sign_up(self):
        url = reverse('user:sign-up')

        response = self.client.post(url, data={
            'username': 'dev@exchange.com',
            'password': '12345678',
            'name': 'Username',
            'country': COUNTRY.PH,
            'referral': ''
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class VerificationTests(APITestCase):
    pass


class ContactTests(APITestCase):
    def setUp(self):
        self.auth_utils = AuthenticationUtils(self.client)
        self.user = self.auth_utils.create_exchange_user()
        self.auth_utils.login()

    def test_add_contact(self):
        url = reverse('user:contact-list')

        response = self.client.post(url, data={
            'name': 'Contact',
            'email': 'contact@contact.com',
            'phone_number': '1234567890',
            'description': 'Some description',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_contact(self):
        contact = ContactFactory(user=self.user)
        url = reverse('user:contact-detail', kwargs={'pk': contact.id})

        response = self.client.put(url, data={
            'name': 'Contact',
            'email': 'contact@contact.com',
            'phone_number': '1234567890',
            'description': 'Some description',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
