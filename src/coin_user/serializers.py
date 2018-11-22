from rest_framework import serializers

from coin_user.models import ExchangeUser, Contact
from common import serializer_fields


class SignUpSerializer(serializers.Serializer):
    username = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    country = serializer_fields.CountryField()


class ExchangeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeUser
        exclude = ('id', 'user', 'email_verification_code', 'phone_verification_code')
        read_only_fields = ('verification_level', 'verification_status')

    email = serializers.CharField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')


class ExchangeUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeUser
        fields = ('phone_number', 'language', 'country', 'currency',
                  'first_name', 'last_name', 'name')
        # extra_kwargs = {
        #     'language': {'required': True},
        #     'country': {'required': True},
        #     'currency': {'required': True},
        #     'first_name': {'required': True},
        #     'last_name': {'required': True},
        # }

    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')


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
