from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import GenericViewSet

from coin_exchange.models import Review, Order
from coin_exchange.serializers import ReviewSerializer
from common.http import StandardPagination


class ReviewViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    queryset = Review.objects.filter(visible=True)
    serializer_class = ReviewSerializer
    pagination_class = StandardPagination

    filter_fields = (
        'country',
        'direction'
    )

    @method_decorator(cache_page(5 * 60))
    def dispatch(self, *args, **kwargs):
        return super(ReviewViewSet, self).dispatch(*args, **kwargs)

    def perform_create(self, serializer):
        order_id = serializer.validated_data['order']
        order = Order.objects.get(pk=order_id)

        exchange_user = self.request.user.exchange_user
        serializer.save(user=exchange_user, country=exchange_user.country, order=order)

        order.reviewed = True
        order.save()
