import logging

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from coin_exchange.models import UserLimit
from coin_system.constants import EMAIL_PURPOSE, SMS_PURPOSE
from coin_system.models import CountryDefaultConfig
from coin_user.constants import VERIFICATION_LEVEL, VERIFICATION_STATUS
from coin_user.exceptions import InvalidVerificationException, AlreadyVerifiedException, NotReadyToVerifyException, \
    ExistedEmailException
from coin_user.models import ExchangeUser
from coin_user.serializers import SignUpSerializer, ExchangeUserSerializer, ExchangeUserProfileSerializer, \
    ExchangeUserIDVerificationSerializer, ExchangeUserSelfieVerificationSerializer, UserSerializer, \
    ResetPasswordSerializer, ChangePasswordSerializer
from common.business import generate_random_code, generate_random_digit
from common.constants import DIRECTION_ALL, CACHE_KEY_FORGOT_PASSWORD
from common.exceptions import InvalidDataException
from notification.email import EmailNotification
from notification.sms import SmsNotification


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        obj = ExchangeUser.objects.get(user=request.user)
        return Response(ExchangeUserSerializer(instance=obj).data)

    def patch(self, request):
        obj = ExchangeUser.objects.select_related('user').get(user=request.user)
        serializer = ExchangeUserProfileSerializer(instance=obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user_serializer = UserSerializer(instance=obj.user, data=request.data, partial=True)
        user_serializer.is_valid(raise_exception=True)

        obj = serializer.save()
        user_serializer.save()

        return Response(ExchangeUserSerializer(instance=obj).data)


class VerifyIDView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        obj = ExchangeUser.objects.get(user=request.user)
        VerifyIDView.check_verified(obj)

        serializer = ExchangeUserIDVerificationSerializer(instance=obj, data=request.data)
        serializer.is_valid(raise_exception=True)

        obj = serializer.save(verification_level=VERIFICATION_LEVEL.level_3,
                              verification_status=VERIFICATION_STATUS.pending)

        return Response(ExchangeUserSerializer(instance=obj).data)

    @staticmethod
    def check_verified(user: ExchangeUser):
        if (user.verification_level > VERIFICATION_LEVEL.level_3) or \
                (user.verification_level == VERIFICATION_LEVEL.level_3 and
                 user.verification_status == VERIFICATION_STATUS.approved):
            raise AlreadyVerifiedException

        if (user.verification_level != VERIFICATION_LEVEL.level_2 and
                user.verification_status == VERIFICATION_STATUS.approved):
            raise NotReadyToVerifyException


class VerifySelfieView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        obj = ExchangeUser.objects.get(user=request.user)
        VerifySelfieView.check_verified(obj)

        serializer = ExchangeUserSelfieVerificationSerializer(instance=obj, data=request.data)
        serializer.is_valid(raise_exception=True)

        obj = serializer.save(verification_level=VERIFICATION_LEVEL.level_4,
                              verification_status=VERIFICATION_STATUS.pending)

        return Response(ExchangeUserSerializer(instance=obj).data)

    @staticmethod
    def check_verified(user: ExchangeUser):
        if (user.verification_level > VERIFICATION_LEVEL.level_4) or \
                (user.verification_level == VERIFICATION_LEVEL.level_4 and
                 user.verification_status == VERIFICATION_STATUS.approved):
            raise AlreadyVerifiedException

        if (user.verification_level != VERIFICATION_LEVEL.level_3 and
                user.verification_status == VERIFICATION_STATUS.approved):
            raise NotReadyToVerifyException


class WalletView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        obj = ExchangeUser.objects.get(user=request.user)
        return Response({'wallet': obj.wallet})

    def put(self, request):
        obj = ExchangeUser.objects.get(user=request.user)
        serializer = ExchangeUserSerializer(instance=obj, data=request.data, partial=True)

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

        if User.objects.filter(username=username).exists():
            raise ExistedEmailException

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

        # Create user limit
        UserLimit.objects.create(user=obj, usage=0, limit=0,
                                 direction=DIRECTION_ALL, fiat_currency=country_config.currency)

        try:
            VerifyEmailView.send_verification_email(obj)
        except Exception as ex:
            logging.exception(ex)

        return Response(ExchangeUserSerializer(instance=obj).data, status=status.HTTP_201_CREATED)


class VerifyEmailView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def put(self, request, format=None):
        verification_code = request.query_params.get('code')
        obj = ExchangeUser.objects.get(user=request.user)

        if obj.verification_level != VERIFICATION_LEVEL.level_1:
            raise InvalidDataException

        if obj.email_verification_code != verification_code:
            raise InvalidVerificationException

        obj.approve_verification()

        return Response(ExchangeUserSerializer(instance=obj).data)

    def post(self, request, format=None):
        obj = ExchangeUser.objects.get(user=request.user)

        VerifyEmailView.send_verification_email(obj)

        return Response(ExchangeUserSerializer(instance=obj).data)

    @staticmethod
    def check_email_verified(user: ExchangeUser):
        if (user.verification_level > VERIFICATION_LEVEL.level_1) or \
                (user.verification_level == VERIFICATION_LEVEL.level_1 and
                 user.verification_status == VERIFICATION_STATUS.approved):
            raise AlreadyVerifiedException

    @staticmethod
    def send_verification_email(user: ExchangeUser):
        verification_code = generate_random_code(16)

        VerifyEmailView.check_email_verified(user)

        user.email_verification_code = verification_code
        user.verification_level = VERIFICATION_LEVEL.level_1
        user.verification_status = VERIFICATION_STATUS.pending
        user.save()

        EmailNotification.send_email_template(user.user.email,
                                              EMAIL_PURPOSE.email_verification,
                                              user.language,
                                              {'code': user.email_verification_code,
                                               'name': user.name})


class VerifyPhoneView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, format=None):
        verification_code = request.query_params.get('code')
        obj = ExchangeUser.objects.get(user=request.user)

        if obj.verification_level != VERIFICATION_LEVEL.level_2:
            raise InvalidDataException

        if obj.phone_verification_code != verification_code:
            raise InvalidVerificationException

        obj.approve_verification()

        return Response(ExchangeUserSerializer(instance=obj).data)

    def post(self, request, format=None):
        obj = ExchangeUser.objects.get(user=request.user)

        self.check_phone_verified(obj)

        if obj.phone_number:
            VerifyPhoneView.send_verification_phone(obj)

        return Response(ExchangeUserSerializer(instance=obj).data)

    @staticmethod
    def check_phone_verified(user: ExchangeUser):
        if (user.verification_level > VERIFICATION_LEVEL.level_2) or \
                (user.verification_level == VERIFICATION_LEVEL.level_2 and
                 user.verification_status == VERIFICATION_STATUS.approved):
            raise AlreadyVerifiedException

    @staticmethod
    def send_verification_phone(user: ExchangeUser):
        verification_code = generate_random_digit(6)

        VerifyPhoneView.check_phone_verified(user)

        user.phone_verification_code = verification_code
        user.verification_level = VERIFICATION_LEVEL.level_2
        user.verification_status = VERIFICATION_STATUS.pending
        user.save()

        SmsNotification.send_sms_template(user.phone_number,
                                          SMS_PURPOSE.phone_verification,
                                          user.language,
                                          {'code': user.phone_verification_code})


class ForgotPasswordView(APIView):
    def post(self, request, format=None):
        data = request.data
        email = data.get('email')
        if not email:
            raise ValidationError

        try:
            obj = ExchangeUser.objects.select_related('user').get(user__email=email)
            code = generate_random_code(36)
            cache.set(CACHE_KEY_FORGOT_PASSWORD.format(code), obj.user.username, timeout=5 * 60)  # Valid in 5 minutes

            EmailNotification.send_email_template(obj.user.email,
                                                  EMAIL_PURPOSE.forgot_password,
                                                  obj.language,
                                                  {'code': code})
        except Exception as ex:
            logging.exception(ex)

        return Response(True)


class ResetPasswordView(APIView):
    def post(self, request, format=None):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(True)
        token = serializer.validated_data['token']
        username = cache.get(CACHE_KEY_FORGOT_PASSWORD.format(token))
        user = User.objects.get(username=username)
        user.set_password(serializer.validated_data['password'])
        user.check_password()

        return Response(True)


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(True)

        user = request.user
        if user.check_password(serializer.validated_data['old_password']):
            user.set_password(serializer.validated_data['password'])
            return Response(True)

        return Response(status=status.HTTP_401_UNAUTHORIZED)
