from django.urls import path, include
from rest_framework.routers import DefaultRouter

from coin_exchange.resource import ReviewViewSet, OrderViewSet, ReferralOrderViewSet, PromotionOrderViewSet
from coin_exchange.views import QuoteView, QuoteReverseView, AddressView, ExpireOrderView, DepositedAddressView, \
    TrackingAddressView, TrackingAddressDetailView, TrackingTransactionView, TrackingTransactionDetailView, \
    ResetUserLimitView, TrackingBitstampTransaction, PayReferralOrderView, TrackingBitstampReferralTransaction

router = DefaultRouter()
router.register('reviews', ReviewViewSet)
router.register('orders', OrderViewSet)
router.register('referrals', ReferralOrderViewSet)
router.register('promotions', PromotionOrderViewSet)

patterns = ([
    path('', include(router.urls)),
    path('quote/', QuoteView.as_view(), name='quote-detail'),
    path('quote-reverse/', QuoteReverseView.as_view(), name='quote-reverse-detail'),
    path('addresses/', AddressView.as_view(), name='address-list'),
    path('deposited-address/', DepositedAddressView.as_view(), name='deposited-address-view'),

    path('expire-order/', ExpireOrderView.as_view(), name='expire-order-view'),
    path('reset-user-limit/', ResetUserLimitView.as_view(), name='reset-user-limit-view'),
    path('tracking-addresses/', TrackingAddressView.as_view(),
         name='tracking-address-list'),
    path('tracking-transactions/', TrackingTransactionView.as_view(),
         name='tracking-transaction-list'),
    path('tracking-addresses/<int:pk>/', TrackingAddressDetailView.as_view(),
         name='tracking-address-detail'),
    path('tracking-transactions/<int:pk>/', TrackingTransactionDetailView.as_view(),
         name='tracking-transaction-detail'),
    path('tracking-bitstamp-transactions/', TrackingBitstampTransaction.as_view(),
         name='tracking-bitstamp-transaction-list'),
    path('pay-referral-order/', PayReferralOrderView.as_view(), name='pay-referral-order-view'),
    path('tracking-bitstamp-referral-transactions/', TrackingBitstampReferralTransaction.as_view(),
         name='tracking-bitstamp-referral-transaction-list'),
], 'exchange')

urlpatterns = [
    path('exchange/', include(patterns)),
]
