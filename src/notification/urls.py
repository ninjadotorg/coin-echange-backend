from django.urls import path, include
from rest_framework.routers import DefaultRouter

from notification.views import NewOrderNotificationView, UserVerificationNotificationView

router = DefaultRouter()

patterns = ([
    path('', include(router.urls)),
    path('new-order-notification/', NewOrderNotificationView.as_view(),
         name='new-order-notification'),
    path('user-verification-notification/', UserVerificationNotificationView.as_view(),
         name='user-verification-notification'),

], 'notification')

urlpatterns = [
    path('notification/', include(patterns)),
]
