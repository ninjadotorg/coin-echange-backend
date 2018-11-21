from django.urls import path, include
from rest_framework.routers import DefaultRouter

from coin_exchange.resource import ReviewViewSet, OrderViewSet
from coin_exchange.views import QuoteView, QuoteReverseView, AddressView, ExpireOrderView, DepositedAddressView

router = DefaultRouter()
router.register('reviews', ReviewViewSet)
router.register('orders', OrderViewSet)

patterns = ([
    path('', include(router.urls)),
    path('quote/', QuoteView.as_view(), name='quote-detail'),
    path('quote-reverse/', QuoteReverseView.as_view(), name='quote-reverse-detail'),
    path('addresses/', AddressView.as_view(), name='address-list'),
    path('expire-order/', ExpireOrderView.as_view(), name='expire-order-view'),
    path('deposited-address/', DepositedAddressView.as_view(), name='deposited-address-view')
], 'exchange')

urlpatterns = [
    path('exchange/', include(patterns)),
]
