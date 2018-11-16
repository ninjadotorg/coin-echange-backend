from django.urls import path, include

from coin_user.views import SignUpView, ProfileView, VerifyEmailView, WalletView, VerifyPhoneView, VerifyIDView, \
    VerifySelfieView

patterns = ([
    path('profile/', ProfileView.as_view(), name='profile'),
    path('wallet/', WalletView.as_view(), name='wallet'),
    path('sign-up/', SignUpView.as_view(), name='sign-up'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('verify-phone/', VerifyPhoneView.as_view(), name='verify-phone'),
    path('verify-id/', VerifyIDView.as_view(), name='verify-id'),
    path('verify-selfie/', VerifySelfieView.as_view(), name='verify-selfie'),
], 'user')

urlpatterns = [
    path('user/', include(patterns)),
]
