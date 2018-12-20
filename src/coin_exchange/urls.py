from django.urls import path, include
from rest_framework.routers import DefaultRouter

from coin_exchange.resource import ReviewViewSet, OrderViewSet, ReferralOrderViewSet, PromotionOrderViewSet
from coin_exchange.views import QuoteView, QuoteReverseView, AddressView, ExpireOrderView, DepositedAddressView, \
    TrackingAddressView, TrackingAddressDetailView, TrackingTransactionView, TrackingTransactionDetailView, \
    ResetUserLimitView, TrackingBitstampTransactionView, PayReferralOrderView, \
    TrackingBitstampReferralTransactionView, TrackingFundTransactionView, TrackingInFundView, TrackingOutFundView, \
    CurrencyView

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
    path('currencies/', CurrencyView.as_view(), name='currencies'),

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
    path('tracking-bitstamp-transactions/', TrackingBitstampTransactionView.as_view(),
         name='tracking-bitstamp-transaction-list'),
    path('pay-referral-order/', PayReferralOrderView.as_view(), name='pay-referral-order-view'),
    path('tracking-bitstamp-referral-transactions/', TrackingBitstampReferralTransactionView.as_view(),
         name='tracking-bitstamp-referral-transaction-list'),
    path('tracking-in-fund/', TrackingInFundView.as_view(),
         name='tracking-in-fund-list'),
    path('tracking-out-fund/', TrackingOutFundView.as_view(),
         name='tracking-out-fund-list'),
    path('tracking-fund-transactions/', TrackingFundTransactionView.as_view(),
         name='tracking-fund-transaction-list'),
], 'exchange')

urlpatterns = [
    path('exchange/', include(patterns)),
]
