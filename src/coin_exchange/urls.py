from django.urls import path, include

from coin_exchange.views import QuoteView

patterns = ([
    path('quote', QuoteView.as_view(), name='quote-detail'),
], 'exchange')

urlpatterns = [
    path('exchange/', include(patterns)),
]
