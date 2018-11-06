from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ViewTests(APITestCase):
    def test_public_view(self):
        url = reverse('misc_check:public_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json()['code'], -1, 'It should be -1')

    def test_protected_view(self):
        username = 'test_user'
        password = 'test_password'

        self.user = User.objects.create_user(
            username=username,
            password=password,
        )
        url = reverse('token:token_obtain_pair')
        token_resp = self.client.post(url, data={
            User.USERNAME_FIELD: username,
            'password': password,
        })
        token = token_resp.json()['access']

        url = reverse('misc_check:protected_view')

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['data']['user'], username)
