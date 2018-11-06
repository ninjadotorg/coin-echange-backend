from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView

patterns = ([
    path('', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('verify', TokenVerifyView.as_view(), name='token_verify'),
], 'token')

urlpatterns = [
    path('token/', include(patterns)),
]
