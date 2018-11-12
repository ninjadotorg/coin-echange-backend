from django.urls import path, include
from rest_framework.routers import DefaultRouter

from coin_exchange.resource import ReviewViewSet
from coin_exchange.views import QuoteView, QuoteReverseView

router = DefaultRouter()
router.register('reviews', ReviewViewSet)

patterns = ([
    path('', include(router.urls)),
    path('quote', QuoteView.as_view(), name='quote-detail'),
    path('quote-reverse', QuoteReverseView.as_view(), name='quote-reverse-detail'),
], 'exchange')

urlpatterns = [
    path('exchange/', include(patterns)),
]
