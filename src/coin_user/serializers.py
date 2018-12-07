from django.contrib.auth.models import User
from rest_framework import serializers

from coin_user.models import ExchangeUser, Contact
from common import serializer_fields


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class SignUpSerializer(serializers.Serializer):
    username = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    name = serializers.CharField()
    country = serializer_fields.CountryField()
    referral = serializers.CharField(allow_blank=True, allow_null=True)


class ExchangeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeUser
        exclude = ('id', 'user', 'email_verification_code', 'phone_verification_code', 'security_2fa_secret',
                   'phone_retry')
        read_only_fields = ('verification_level', 'verification_status', 'payment_verification_status',
                            'security_2fa', 'pending_phone_number')

    email = serializers.CharField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')


class ExchangeUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeUser
        fields = ('language', 'currency',
                  'first_name', 'last_name', 'payment_info')

    first_name = serializers.CharField()
    last_name = serializers.CharField()


class ExchangeUserIDVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeUser
        fields = ('id_name', 'id_number', 'id_type', 'front_image', 'back_image')
        extra_kwargs = {
            'id_name': {'required': True},
            'id_number': {'required': True},
            'id_type': {'required': True},
            'front_image': {'required': True},
            'back_image': {'required': True},
        }


class ExchangeUserSelfieVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeUser
        fields = ('selfie_image', )
        extra_kwargs = {
            'selfie_image': {'required': True},
        }


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        exclude = ('user', )


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    password = serializers.CharField(min_length=8, write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=8, write_only=True)
    password = serializers.CharField(min_length=8, write_only=True)


class VerifyPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, write_only=True)
