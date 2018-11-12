from rest_framework import mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from coin_exchange.business.crypto import AddressManagement
from coin_exchange.business.quote import QuoteManagement
from coin_exchange.models import Order
from coin_exchange.serializers import OrderSerializer
from common.business import view_serializer_fields
from common.constants import CURRENCY


class OrderView(mixins.CreateModelMixin,
                mixins.RetrieveModelMixin,
                mixins.UpdateModelMixin,
                mixins.ListModelMixin,
                GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Order.objects.none()
    filter_fields = (
        'direction',
        'order_type'
    )

    def perform_create(self, serializer):
        # Do more complex validation here to re-use the data for saving

        serializer.save(user=self.request.user.exchange_user)

    def get_queryset(self):
        qs = Order.objects.filter(user__user=self.request.user)

        return qs


class AddressView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        currency = request.query_params.get('currency')
        if currency not in CURRENCY:
            raise ValidationError

        address, exists = AddressManagement.create_address(request.user.exchange_user, currency)
        return Response(address, status=status.HTTP_200_OK if exists else status.HTTP_201_CREATED)


class QuoteView(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        serializer = QuoteManagement.get_quote(request.user, request.query_params)
        view_fields = ['amount', 'currency', 'fiat_currency', 'direction', 'fiat_local_currency',
                       'fiat_amount', 'fiat_local_amount',
                       'fiat_amount_cod', 'fiat_local_amount_cod']

        return Response(view_serializer_fields(view_fields, serializer.validated_data))


class QuoteReverseView(APIView):
    def get(self, request, format=None):
        serializer = QuoteManagement.get_quote_reverse(request.user, request.query_params)
        view_fields = ['amount', 'currency', 'fiat_currency', 'direction', 'fiat_local_currency',
                       'fiat_amount', 'fiat_local_amount',
                       ]

        return Response(view_serializer_fields(view_fields, serializer.validated_data))
