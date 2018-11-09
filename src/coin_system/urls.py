from django.urls import path, include
from rest_framework.routers import DefaultRouter

from coin_system.resource import BankViewSet

router = DefaultRouter()
router.register('banks', BankViewSet)

patterns = ([
    path('', include(router.urls))
], 'system')

urlpatterns = [
    path('system/', include(patterns)),
]
