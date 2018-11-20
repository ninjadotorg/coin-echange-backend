from rest_framework.response import Response
from rest_framework.views import APIView

from coin_exchange.constants import CONFIG_USER_LIMIT
from coin_system.models import Config
from common.business import PriceManagement, RateManagement
from common.constants import CURRENCY


class CurrencyRateView(APIView):
    def post(self, request, format=None):
        RateManagement.save_rates()

        return Response(True)


class CryptoRateView(APIView):
    def post(self, request, format=None):
        for currency in CURRENCY:
            PriceManagement.save_cache_price(currency)

        return Response(True)


class CurrencyLevelLimitView(APIView):
    def get(self, request, format=None):
        currency = request.params.get('currency', '')
        keys = Config.objects.filter(key__istartswith=currency).order_by('key')
        limits = list(map(lambda key: {'currency': key.key.split(CONFIG_USER_LIMIT)[0],
                                       'level': key.key.split(CONFIG_USER_LIMIT)[1],
                                       'limit': key.value,
                                       }, keys))

        return Response(limits)
