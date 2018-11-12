from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets

from coin_system.models import Bank, PopularPlace, CountryCurrency
from coin_system.serializers import BankSerializer, PopularPlaceSerializer, CountryCurrencySerializer


class BankViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bank.objects.filter(active=True)
    serializer_class = BankSerializer
    filterset_fields = (
        'country',
        'currency'
    )

    @method_decorator(cache_page(5*60))
    def dispatch(self, *args, **kwargs):
        return super(BankViewSet, self).dispatch(*args, **kwargs)


class CountryCurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CountryCurrency.objects.filter(active=True)
    serializer_class = CountryCurrencySerializer
    filterset_fields = (
        'country',
    )

    @method_decorator(cache_page(5*60))
    def dispatch(self, *args, **kwargs):
        return super(CountryCurrencyViewSet, self).dispatch(*args, **kwargs)


class PopularPlaceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PopularPlace.objects.filter(active=True)
    serializer_class = PopularPlaceSerializer
    filterset_fields = (
        'country',
    )

    @method_decorator(cache_page(5*60))
    def dispatch(self, *args, **kwargs):
        return super(PopularPlaceViewSet, self).dispatch(*args, **kwargs)
