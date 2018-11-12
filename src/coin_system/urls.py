from django.urls import path, include
from rest_framework.routers import DefaultRouter

from coin_system.resource import BankViewSet, PopularPlaceViewSet, CountryCurrencyViewSet
from coin_system.views import CurrencyRateView, CryptoRateView

router = DefaultRouter()
router.register('banks', BankViewSet)
router.register('popular-places', PopularPlaceViewSet)
router.register('country-currencies', CountryCurrencyViewSet)

patterns = ([
    path('', include(router.urls)),
    path('currency-rates', CurrencyRateView.as_view(), name='currency-rates'),
    path('crypto-rates', CryptoRateView.as_view(), name='crypto-rates'),
], 'system')

urlpatterns = [
    path('system/', include(patterns)),
]
