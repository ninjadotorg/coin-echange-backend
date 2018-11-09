from django.urls import path, include
from rest_framework.routers import DefaultRouter

from coin_system.resource import BankViewSet, PopularPlaceViewSet, CountryCurrencyViewSet

router = DefaultRouter()
router.register('banks', BankViewSet)
router.register('popular-places', PopularPlaceViewSet)
router.register('country-currencies', CountryCurrencyViewSet)

patterns = ([
    path('', include(router.urls))
], 'system')

urlpatterns = [
    path('system/', include(patterns)),
]
