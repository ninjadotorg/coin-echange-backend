from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from coin_system.models import CountryDefaultConfig
from coin_user.models import ExchangeUser
from coin_user.serializers import SignUpSerializer, ExchangeUserSerializer
from common.exceptions import InvalidDataException


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
            is_active=False,
        )

        country_config = CountryDefaultConfig.objects.filter(country=country).first()
        if country_config is None:
            raise InvalidDataException

        obj = ExchangeUser.objects.create(user=user,
                                          name='{} {}'.format(first_name, last_name),
                                          language=country_config.language,
                                          country=country_config.country,
                                          currency=country_config.currency)

        # TODO: Send email verification

        return Response(ExchangeUserSerializer(instance=obj).data, status=status.HTTP_201_CREATED)
