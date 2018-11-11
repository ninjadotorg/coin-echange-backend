from django.urls import path, include

from coin_exchange.views import QuoteView, QuoteReverseView

patterns = ([
    path('quote', QuoteView.as_view(), name='quote-detail'),
    path('quote-reverse', QuoteReverseView.as_view(), name='quote-reverse-detail'),
], 'exchange')

urlpatterns = [
    path('exchange/', include(patterns)),
]
