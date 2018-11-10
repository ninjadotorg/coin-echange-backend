import logging

from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from coin_exchange.constants import FEE_COIN_ORDER_COD, FEE_COIN_ORDER_BANK
from coin_exchange.exceptions import CoinUserOverLimitException, CoinOverLimitException
from coin_exchange.models import Order, UserLimit, Pool
from coin_exchange.serializers import OrderSerializer, QuoteSerializer, QuoteInputSerializer
from coin_system.business import markup_fee, round_currency
from common.business import PriceManagement, RateManagement, view_serializer_fields
from common.constants import FIAT_CURRENCY, DIRECTION
from common.exceptions import InvalidDataException


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


class QuoteView(APIView):
    def get(self, request, format=None):
        serializer = QuoteView.get_quote(request, request.query_params)
        view_fields = ['amount', 'currency', 'fiat_currency', 'fiat_local_currency',
                       'fiat_amount', 'fiat_local_amount',
                       'fiat_amount_cod', 'fiat_local_amount_cod']

        return Response(view_serializer_fields(view_fields, serializer.validated_data))

    @staticmethod
    def get_quote(user, params) -> QuoteSerializer:
        input_serializer = QuoteInputSerializer(data={
            'amount': params.get('amount'),
            'currency': params.get('currency'),
            'fiat_currency': params.get('fiat_currency', FIAT_CURRENCY.USD),
            'pool_check': params.get('check', False),
            'user_check': params.get('user_check', False),
        })

        if input_serializer.is_valid(raise_exception=True):
            safe_data = input_serializer.validated_data

            amount = safe_data['amount']
            price = PriceManagement.get_cache_price(safe_data['currency'])

            raw_fiat_amount = amount * price
            fiat_local_currency = safe_data['fiat_currency']
            local_price = RateManagement.convert_to_local_currency(raw_fiat_amount, fiat_local_currency)

            if safe_data['user_check']:
                # request.user
                # User logged in
                if user:
                    # Get user limit to check
                    try:
                        user_limit = UserLimit.objects.get(user__user=user, direction=DIRECTION.buy,
                                                           fiat_currency=safe_data['fiat_currency'])
                        if user_limit.usage + local_price > user_limit.limit:
                            raise CoinUserOverLimitException
                    except UserLimit.DoesNotExist as e:
                        logging.exception(e)
                        raise InvalidDataException

            if safe_data['pool_check']:
                pool = Pool.objects.get(direction=DIRECTION.buy,
                                        currency=safe_data['currency'])
                if pool.usage + amount > pool.limit:
                    raise CoinOverLimitException

            fiat_amount, fiat_amount_fee = markup_fee(price, FEE_COIN_ORDER_BANK)
            fiat_amount_cod, fiat_amount_fee_cod = markup_fee(price, FEE_COIN_ORDER_COD)
            fiat_local_amount = RateManagement.convert_to_local_currency(fiat_amount, fiat_local_currency)
            fiat_local_amount_cod = RateManagement.convert_to_local_currency(fiat_amount_cod, fiat_local_currency)
            fee_local = RateManagement.convert_to_local_currency(fiat_amount_fee, fiat_local_currency)
            fee_local_cod = RateManagement.convert_to_local_currency(fiat_amount_fee_cod, fiat_local_currency)

            serializer = QuoteSerializer(data={
                'fiat_amount': round_currency(fiat_amount),
                'fiat_currency': FIAT_CURRENCY.USD,
                'fiat_local_amount': round_currency(fiat_local_amount),
                'fiat_local_currency': fiat_local_currency,
                'fiat_amount_cod': round_currency(fiat_amount_cod),
                'fiat_local_amount_cod': round_currency(fiat_local_amount_cod),
                'fee': round_currency(fiat_amount_fee),
                'fee_cod': round_currency(fiat_amount_fee_cod),
                'fee_local': round_currency(fee_local),
                'fee_local_cod': round_currency(fee_local_cod),
                'raw_fiat_amount': round_currency(raw_fiat_amount),
                'price': round_currency(price),
                'amount': amount,
                'currency': safe_data['currency']
            })
            serializer.is_valid(raise_exception=True)

            return serializer
