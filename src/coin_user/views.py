import logging

from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from coin_system.constants import EMAIL_PURPOSE
from coin_system.models import CountryDefaultConfig
from coin_user.constants import VERIFICATION_LEVEL, VERIFICATION_STATUS
from coin_user.exceptions import InvalidVerificationException, AlreadyVerifiedException
from coin_user.models import ExchangeUser
from coin_user.serializers import SignUpSerializer, ExchangeUserSerializer
from common.business import generate_random_code
from common.exceptions import InvalidDataException
from notification.email import EmailNotification


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        obj = ExchangeUser.objects.get(user=request.user)
        return Response(ExchangeUserSerializer(instance=obj).data)


class WalletView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        obj = ExchangeUser.objects.get(user=request.user)
        return Response({'wallet': obj.wallet})

    def put(self, request):
        obj = ExchangeUser.objects.get(user=request.user)
        serializer = SignUpSerializer(instance=obj, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        return Response({'wallet': obj.wallet})


class SignUpView(APIView):
    @transaction.atomic
    def post(self, request, format=None):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(True)

        username = serializer.validated_data['username']
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']
        country = serializer.validated_data['country']
        user = User.objects.create_user(
            username=username,
            password=serializer.validated_data['password'],
            email=username,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )

        country_config = CountryDefaultConfig.objects.filter(country=country).first()
        if country_config is None:
            raise InvalidDataException

        obj = ExchangeUser.objects.create(user=user,
                                          name='{} {}'.format(first_name, last_name),
                                          language=country_config.language,
                                          country=country_config.country,
                                          currency=country_config.currency)

        try:
            VerifyEmailView.send_verification_email(obj)
        except Exception as ex:
            logging.exception(ex)

        return Response(ExchangeUserSerializer(instance=obj).data, status=status.HTTP_201_CREATED)


class VerifyEmailView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, format=None):
        verification_code = request.query_params.get('code')
        obj = ExchangeUser.objects.get(user=request.user)
        if obj.email_verification_code != verification_code:
            raise InvalidVerificationException

        obj.verification_level = VERIFICATION_LEVEL.level_1
        obj.verification_status = VERIFICATION_STATUS.approved
        obj.save()

        return Response(ExchangeUserSerializer(instance=obj).data)

    def post(self, request, format=None):
        obj = ExchangeUser.objects.get(user=request.user)

        self.check_email_verified(obj)

        VerifyEmailView.send_verification_email(obj)

        return Response(ExchangeUserSerializer(instance=obj).data)

    @staticmethod
    def check_email_verified(user: ExchangeUser):
        if user.verification_level > VERIFICATION_LEVEL.level_1:
            raise AlreadyVerifiedException

    @staticmethod
    def send_verification_email(user: ExchangeUser):
        verification_code = generate_random_code(16)

        VerifyEmailView.check_email_verified(user)

        user.email_verification_code = verification_code
        user.save()

        EmailNotification.send_email_template(user.user.email,
                                              EMAIL_PURPOSE.email_verification,
                                              user.language,
                                              {'code': user.email_verification_code})
