from django.urls import path, include
from rest_framework.routers import DefaultRouter

from coin_system.resource import BankViewSet, PopularPlaceViewSet, PopularBankViewSet, \
    CountryCurrencyViewSet, CountryDefaultConfigViewSet, ContactViewSet
from coin_system.views import CurrencyRateView, CryptoRateView, CurrencyLevelLimitView, LanguageView, ComparePrice

router = DefaultRouter()
router.register('banks', BankViewSet)
router.register('popular-places', PopularPlaceViewSet)
router.register('popular-banks', PopularBankViewSet)
router.register('country-currencies', CountryCurrencyViewSet)
router.register('country-default-configs', CountryDefaultConfigViewSet)
router.register('contacts', ContactViewSet)

patterns = ([
    path('', include(router.urls)),
    path('currency-rates/', CurrencyRateView.as_view(), name='currency-rates'),
    path('crypto-rates/', CryptoRateView.as_view(), name='crypto-rates'),
    path('currency-level-limits/', CurrencyLevelLimitView.as_view(), name='currency-level-limits'),
    path('languages/', LanguageView.as_view(), name='languages'),
    path('compare-price/', ComparePrice.as_view(), name='compare-price'),
], 'system')

urlpatterns = [
    path('system/', include(patterns)),
]
