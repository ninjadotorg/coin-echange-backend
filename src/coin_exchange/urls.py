from django.urls import path

from coin_exchange.views import ProtectedView

urlpatterns = [
    path('protected-view', ProtectedView.as_view(), name='protected_view'),
]
