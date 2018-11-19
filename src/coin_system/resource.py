from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, mixins
from rest_framework.viewsets import GenericViewSet

from coin_system.models import Bank, PopularPlace, CountryCurrency, CountryDefaultConfig, LandingPageContact
from coin_system.serializers import BankSerializer, PopularPlaceSerializer, CountryCurrencySerializer, \
    CountryDefaultConfigSerializer, ContactSerializer


class BankViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bank.objects.filter(active=True)
    serializer_class = BankSerializer
    filterset_fields = (
        'country',
        'currency'
    )

    # @method_decorator(cache_page(5*60))
    def dispatch(self, *args, **kwargs):
        return super(BankViewSet, self).dispatch(*args, **kwargs)


class CountryCurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CountryCurrency.objects.filter(active=True)
    serializer_class = CountryCurrencySerializer
    filterset_fields = (
        'country',
    )

    # @method_decorator(cache_page(5*60))
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


class CountryDefaultConfigViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CountryDefaultConfig.objects.filter(active=True)
    serializer_class = CountryDefaultConfigSerializer

    @method_decorator(cache_page(5*60))
    def dispatch(self, *args, **kwargs):
        return super(CountryDefaultConfigViewSet, self).dispatch(*args, **kwargs)


class ContactViewSet(mixins.CreateModelMixin,
                     GenericViewSet):
    serializer_class = ContactSerializer
    queryset = LandingPageContact.objects.none()
