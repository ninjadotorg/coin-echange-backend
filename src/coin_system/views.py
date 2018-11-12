from rest_framework.response import Response
from rest_framework.views import APIView

from common.business import PriceManagement, RateManagement
from common.constants import CURRENCY


class CurrencyRateView(APIView):
    def post(self, request, format=None):
        RateManagement.save_rates()

        return Response(True)


class CryptoRateView(APIView):
    def post(self, request, format=None):
        for currency in [CURRENCY.BTC, CURRENCY.ETH]:
            PriceManagement.save_cache_price(currency)

        return Response(True)
