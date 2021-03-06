import logging

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from coin_exchange.business.crypto import AddressManagement, TrackingManagement
from coin_exchange.business.fund import FundManagement
from coin_exchange.business.order import OrderManagement
from coin_exchange.business.quote import QuoteManagement
from coin_exchange.business.referral import ReferralManagement
from common.business import view_serializer_fields
from common.constants import SUPPORT_CURRENCIES
from common.exceptions import InvalidInputDataException


class AddressView(APIView):
    authentication_classes = (JWTAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        currency = request.query_params.get('currency')
        if currency not in SUPPORT_CURRENCIES:
            raise InvalidInputDataException

        address, exists = AddressManagement.create_address(request.user.exchange_user, currency)
        return Response(address, status=status.HTTP_200_OK if exists else status.HTTP_201_CREATED)


class QuoteView(APIView):
    authentication_classes = (JWTAuthentication, TokenAuthentication)

    def get(self, request, format=None):
        serializer = QuoteManagement.get_quote(request.user, request.query_params)
        view_fields = ['amount', 'currency', 'fiat_currency', 'direction', 'fiat_local_currency',
                       'fiat_amount', 'fiat_local_amount',
                       'fiat_amount_cod', 'fiat_local_amount_cod']

        return Response(view_serializer_fields(view_fields, serializer.validated_data))


class QuoteReverseView(APIView):
    authentication_classes = (JWTAuthentication, TokenAuthentication)

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


class CurrencyView(APIView):
    def get(self, request, format=None):
        return Response(SUPPORT_CURRENCIES)


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


class TrackingBitstampTransactionView(APIView):
    def post(self, request, format=None):
        OrderManagement.load_transferring_order_to_track()
        return Response()


class PayReferralOrderView(APIView):
    def post(self, request, format=None):
        ReferralManagement.pay_referral()
        return Response()


class TrackingBitstampReferralTransactionView(APIView):
    def post(self, request, format=None):
        ReferralManagement.load_transferring_referral_to_track()
        return Response()


class TrackingInFundView(APIView):
    def post(self, request, format=None):
        try:
            for curr in SUPPORT_CURRENCIES:
                FundManagement.update_in_fund(curr)
        except Exception as ex:
            logging.exception(ex)
        return Response()


class TrackingOutFundView(APIView):
    def post(self, request, format=None):
        try:
            for curr in SUPPORT_CURRENCIES:
                FundManagement.update_out_fund(curr)
        except Exception as ex:
            logging.exception(ex)
        return Response()


class TrackingFundTransactionView(APIView):
    def post(self, request, format=None):
        FundManagement.track_transferring()
        return Response()
