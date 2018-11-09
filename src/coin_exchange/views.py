from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from coin_exchange.models import Order
from coin_exchange.serializers import OrderSerializer, QuoteSerializer, QuoteInputSerializer
from common.constants import FIAT_CURRENCY


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
        params = request.query_params
        input_serializer = QuoteInputSerializer(data={
            'amount': params.get('amount'),
            'currency': params.get('currency'),
            'fiat_currency': params.get('fiat_currency', FIAT_CURRENCY.USD),
            'pool_check': params.get('check', False),
            'user_check': params.get('user_check', False),
        })

        if input_serializer.is_valid(raise_exception=True):
            if input_serializer.validated_data['user_check']:
                # User logged in
                if request.user:
                    # Get user limit to check
                    # request.user
                    pass

        serializer = QuoteSerializer(data={
            'fiat_amount': '1',
            'fiat_currency': 'VND',
            'fiat_local_amount': '1',
            'fiat_local_currency': 'VND',
            'fiat_amount_cod': '1',
            'fiat_local_amount_cod': '1',
            'price': '1',
        })
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)
