from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from coin_system.models import Bank
from coin_system.serializers import BankSerializer


class BankViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bank.objects.filter(active=True)
    serializer_class = BankSerializer

    filter_backends = (DjangoFilterBackend,)
    filter_fields = (
        'country',
        'currency'
    )
