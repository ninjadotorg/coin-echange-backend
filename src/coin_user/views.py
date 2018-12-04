import logging
import uuid

import pyotp
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import transaction
from django.db.models import F
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from coin_exchange.business.user_limit import update_currency
from coin_exchange.models import UserLimit
from integration.google_storage import upload_file
from notification.constants import EMAIL_PURPOSE, SMS_PURPOSE
from coin_system.models import CountryDefaultConfig
from coin_user.constants import VERIFICATION_LEVEL, VERIFICATION_STATUS
from coin_user.exceptions import InvalidVerificationException, AlreadyVerifiedException, NotReadyToVerifyException, \
    ExistedEmailException, ResetPasswordExpiredException, InvalidPasswordException, NotYetVerifiedException, \
    ExistedNameException, ExceedLimitException
from coin_user.models import ExchangeUser
from coin_user.serializers import SignUpSerializer, ExchangeUserSerializer, ExchangeUserProfileSerializer, \
    ExchangeUserIDVerificationSerializer, ExchangeUserSelfieVerificationSerializer, UserSerializer, \
    ResetPasswordSerializer, ChangePasswordSerializer
from common.business import generate_random_code, generate_random_digit, Is2FA
from common.constants import DIRECTION_ALL, CACHE_KEY_FORGOT_PASSWORD
from common.exceptions import InvalidDataException, InvalidInputDataException
from notification.provider.email import EmailNotification
from notification.provider.sms import SmsNotification


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        obj = ExchangeUser.objects.get(user=request.user)
        return Response(ExchangeUserSerializer(instance=obj).data)

    @transaction.atomic
    def patch(self, request):
        obj = ExchangeUser.objects.select_related('user').get(user=request.user)

        old_currency = obj.currency
        old_payment_info = obj.payment_info

        serializer = ExchangeUserProfileSerializer(instance=obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user_serializer = UserSerializer(instance=obj.user, data=request.data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        if user_serializer.validated_data.get('currency') and \
                old_currency != user_serializer.validated_data.get('currency'):
            update_currency(obj, user_serializer.validated_data['currency'])

        if user_serializer.validated_data.get('payment_info') and \
                old_payment_info != user_serializer.validated_data.get('payment_info'):
            obj.change_payment_verification(save=False)

        obj = serializer.save()
        user_serializer.save()

        return Response(ExchangeUserSerializer(instance=obj).data)


class VerifyIDView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        obj = ExchangeUser.objects.get(user=request.user)
        VerifyIDView.check_last_step_verified(obj)
        VerifyIDView.check_verified(obj)

        serializer = ExchangeUserIDVerificationSerializer(instance=obj, data=request.data)
        serializer.is_valid(raise_exception=True)

        obj = serializer.save(verification_level=VERIFICATION_LEVEL.level_3,
                              verification_status=VERIFICATION_STATUS.pending)

        return Response(ExchangeUserSerializer(instance=obj).data)

    @staticmethod
    def check_last_step_verified(user: ExchangeUser):
        if user.verification_level < VERIFICATION_LEVEL.level_2 and \
                user.verification_status != VERIFICATION_STATUS.approved:
            raise NotYetVerifiedException

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
        VerifySelfieView.check_last_step_verified(obj)
        VerifySelfieView.check_verified(obj)

        serializer = ExchangeUserSelfieVerificationSerializer(instance=obj, data=request.data)
        serializer.is_valid(raise_exception=True)

        obj = serializer.save(verification_level=VERIFICATION_LEVEL.level_4,
                              verification_status=VERIFICATION_STATUS.pending)

        return Response(ExchangeUserSerializer(instance=obj).data)

    @staticmethod
    def check_last_step_verified(user: ExchangeUser):
        if user.verification_level < VERIFICATION_LEVEL.level_2 and \
                user.verification_status != VERIFICATION_STATUS.approved:
            raise NotYetVerifiedException

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
        # first_name = serializer.validated_data['first_name']
        # last_name = serializer.validated_data['last_name']
        name = serializer.validated_data['name']
        country = serializer.validated_data['country']

        if User.objects.filter(username=username).exists():
            raise ExistedEmailException
        if ExchangeUser.objects.filter(name__exact=name).exists():
            raise ExistedNameException

        referral_name = serializer.validated_data.get('referral')
        referral_user = ExchangeUser.objects.filter(name__exact=referral_name).first()

        user = User.objects.create_user(
            username=username,
            password=serializer.validated_data['password'],
            email=username,
            # first_name=first_name,
            # last_name=last_name,
            is_active=True,
        )

        country_config = CountryDefaultConfig.objects.filter(country=country).first()
        if country_config is None:
            raise InvalidDataException

        obj = ExchangeUser.objects.create(user=user,
                                          name=name,
                                          language=country_config.language,
                                          country=country_config.country,
                                          currency=country_config.currency,
                                          referral=referral_user)

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

    @transaction.atomic
    def put(self, request, format=None):
        verification_code = request.query_params.get('code')
        obj = ExchangeUser.objects.get(user=request.user)

        self.check_last_step_verified(obj)
        if not obj.pending_phone_number:
            raise InvalidDataException

        if obj.phone_verification_code != verification_code:
            raise InvalidVerificationException

        verified = False
        try:
            self.check_phone_verified(obj)
        except AlreadyVerifiedException:
            verified = True
            if not obj.pending_phone_number:
                raise

        obj.phone_number = obj.pending_phone_number
        obj.pending_phone_number = ''
        if not verified:
            obj.approve_verification()
        else:
            obj.save(update_fields=['phone_number', 'pending_phone_number'])

        return Response(ExchangeUserSerializer(instance=obj).data)

    def post(self, request, format=None):
        obj = ExchangeUser.objects.get(user=request.user)

        phone_number = request.data.get('phone_number')
        if not phone_number:
            raise ValidationError

        self.check_last_step_verified(obj)
        verified = False
        try:
            self.check_phone_verified(obj)
        except AlreadyVerifiedException:
            raise
            # === WHEN want to verify another phone, remove these line
            # verified = True
            # only check if the phone submit is the same with the current one
            # if obj.phone_number == phone_number:
            #     raise

        VerifyPhoneView.send_verification_phone(obj, phone_number, verified)

        return Response(ExchangeUserSerializer(instance=obj).data)

    @staticmethod
    def check_last_step_verified(user: ExchangeUser):
        if user.verification_level < VERIFICATION_LEVEL.level_1 and \
                user.verification_status != VERIFICATION_STATUS.approved:
            raise NotYetVerifiedException

    @staticmethod
    def check_phone_verified(user: ExchangeUser):
        if (user.verification_level > VERIFICATION_LEVEL.level_2) or \
                (user.verification_level == VERIFICATION_LEVEL.level_2 and
                 user.verification_status == VERIFICATION_STATUS.approved):
            raise AlreadyVerifiedException

    @staticmethod
    def send_verification_phone(user: ExchangeUser, phone_number: str, verified: bool):
        if user.phone_retry <= 0:
            raise ExceedLimitException

        verification_code = generate_random_digit(6)
        user.pending_phone_number = phone_number
        user.phone_verification_code = verification_code
        user.phone_retry = F('phone_retry') - 1
        if not verified:
            user.verification_level = VERIFICATION_LEVEL.level_2
            user.verification_status = VERIFICATION_STATUS.pending
        user.save()

        SmsNotification.send_sms_template(phone_number,
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
            cache.set(CACHE_KEY_FORGOT_PASSWORD.format(code), obj.user.username, timeout=15 * 60)  # Valid in 15 minutes

            EmailNotification.send_email_template(obj.user.email,
                                                  EMAIL_PURPOSE.forgot_password,
                                                  obj.language,
                                                  {'code': code,
                                                   'email': email,
                                                   'name': obj.user.get_full_name()})
        except Exception as ex:
            logging.exception(ex)

        return Response(True)


class ResetPasswordView(APIView):
    def post(self, request, format=None):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(True)
        token = serializer.validated_data['token']
        username = cache.get(CACHE_KEY_FORGOT_PASSWORD.format(token))
        if username:
            user = User.objects.get(username=username)
            user.set_password(serializer.validated_data['password'])
            user.save()

            return Response(True)
        else:
            raise ResetPasswordExpiredException


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(True)

        user = request.user
        if user.check_password(serializer.validated_data['old_password']):
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response(True)

        raise InvalidPasswordException


class TwoFAView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        obj = request.user.exchange_user
        if not obj.security_2fa:
            obj.security_2fa_secret = pyotp.random_base32()
            obj.save(update_fields=['security_2fa_secret'])

            return Response({'otp': pyotp.totp.TOTP(obj.security_2fa_secret).provisioning_uri(
                request.user.email,
                issuer_name=settings.EMAIL_FROM_NAME)})

        return Response({'detail': 'Already setup'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        if not Is2FA.check(request):
            return Response(status=status.HTTP_403_FORBIDDEN)

        obj = request.user.exchange_user
        obj.security_2fa = True
        obj.save(update_fields=['security_2fa'])

        return Response(True)

    def delete(self, request, format=None):
        if not Is2FA.check(request):
            return Response(status=status.HTTP_403_FORBIDDEN)

        obj = request.user.exchange_user
        obj.security_2fa = False
        obj.security_2fa_secret = ''
        obj.save(update_fields=['security_2fa', 'security_2fa_secret'])

        return Response(True)


class ReferralView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        obj = ExchangeUser.objects.prefetch_related('referral_users__user').get(user=request.user)
        referrals = obj.referral_users.all()

        return Response([{
            'name': item.name,
            'status': 'finished' if item.first_purchase else 'unfinished',
            'date_joined': item.user.date_joined,
        } for item in referrals])


class FileUploadView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_class = (FileUploadParser,)

    def post(self, request, format=None):
        if 'file' not in request.data:
            raise InvalidInputDataException
        if request.query_params.get('type', '') not in ['verification', 'receipt']:
            raise InvalidInputDataException
        file_type = request.query_params['type']

        f = request.data['file']
        ext = f.name.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(uuid.uuid4().hex, ext)
        blob = upload_file('{}/{}'.format(file_type, filename), f)

        return Response({'url': blob.public_url})
