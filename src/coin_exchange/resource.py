from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from coin_exchange.business.order import OrderManagement
from coin_exchange.constants import ORDER_STATUS, ORDER_TYPE
from coin_exchange.exceptions import InvalidOrderStatusException
from coin_exchange.models import Review, Order
from coin_exchange.serializers import ReviewSerializer, OrderSerializer, SellingOrderSerializer
from common.constants import DIRECTION
from common.http import StandardPagination


class ReviewViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ReviewSerializer
    pagination_class = StandardPagination
    queryset = Review.objects.filter(visible=True).order_by('-created_at')

    filterset_fields = (
        'country',
        'direction'
    )

    @method_decorator(cache_page(5 * 60))
    def dispatch(self, *args, **kwargs):
        return super(ReviewViewSet, self).dispatch(*args, **kwargs)

    def perform_create(self, serializer):
        order = serializer.validated_data['order']

        exchange_user = self.request.user.exchange_user
        serializer.save(user=exchange_user, country=exchange_user.country, order=order, direction=order.direction)

        order.reviewed = True
        order.save()


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer
    pagination_class = StandardPagination
    queryset = Order.objects.none()

    filterset_fields = (
        'direction',
        'order_type'
    )

    def create(self, request, *args, **kwargs):
        direction = request.data.get('direction')
        if direction == DIRECTION.sell:
            serializer = SellingOrderSerializer(data=request.data)
            serializer.is_valid(True)

            OrderManagement.add_selling_order(self.request.user, serializer)
        else:
            serializer = OrderSerializer(data=request.data)
            serializer.is_valid(True)

            OrderManagement.add_order(self.request.user, serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'])
    def receipt(self, request, pk=None):
        # order = self.get_object()
        order = Order.objects.get(pk=pk)
        serializer = OrderSerializer(order, data={'receipt_url': request.data.get('receipt_url')}, partial=True)
        serializer.is_valid(True)
        if order.order_type == ORDER_TYPE.bank and order.status == ORDER_STATUS.pending \
                and order.user.user == request.user:
            serializer.save(status=ORDER_STATUS.fiat_transferring)
        else:
            raise InvalidOrderStatusException

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        OrderManagement.cancel_order(request.user, order)

        return Response(status=status.HTTP_200_OK)

    def get_queryset(self):
        qs = Order.objects.filter(user__user=self.request.user).order_by('-created_at')

        return qs
