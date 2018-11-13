from rest_framework import serializers

from coin_user.models import ExchangeUser
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
        exclude = ('id', 'user')
        read_only_fields = ('verification_level', 'verification_status')
