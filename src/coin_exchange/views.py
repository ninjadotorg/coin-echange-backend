from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from coin_exchange.business.crypto import AddressManagement, TrackingManagement
from coin_exchange.business.notification import NotificationManagement
from coin_exchange.business.order import OrderManagement
from coin_exchange.business.quote import QuoteManagement
from common.business import view_serializer_fields
from common.constants import SUPPORT_CURRENCIES


class AddressView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        currency = request.query_params.get('currency')
        if currency not in SUPPORT_CURRENCIES:
            raise ValidationError

        address, exists = AddressManagement.create_address(request.user.exchange_user, currency)
        return Response(address, status=status.HTTP_200_OK if exists else status.HTTP_201_CREATED)


class QuoteView(APIView):
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


class ExpireOrderView(APIView):
    def post(self, request, format=None):
        OrderManagement.expire_order()
        return Response()


class ResetUserLimitView(APIView):
    def post(self, request, format=None):
        OrderManagement.reset_user_limit()
        return Response()


class DepositedAddressView(APIView):
    def get(self, request, format=None):
        currency = request.query_params.get('currency', '')
        if currency not in SUPPORT_CURRENCIES:
            raise ValidationError
        address = request.query_params.get('address', '')
        if not address:
            raise ValidationError

        has_transaction = len(TrackingManagement.track_network_address(address, currency).tx_hashes) > 0

        return Response({'has_transaction': has_transaction})


class TrackingAddressView(APIView):
    def post(self, request, format=None):
        TrackingManagement.load_tracking_address()
        return Response()


class TrackingAddressDetailView(APIView):
    def post(self, request, pk, format=None):
        TrackingManagement.track_system_address(pk)
        return Response()


class TrackingTransactionView(APIView):
    def post(self, request, format=None):
        TrackingManagement.load_tracking_transaction()
        return Response()


class TrackingTransactionDetailView(APIView):
    def post(self, request, pk, format=None):
        TrackingManagement.track_system_transaction(pk)
        return Response()


class NewOrderNotification(APIView):
    def post(self, request, format=None):
        NotificationManagement.send_new_order_notification(request.data)
        return Response()
