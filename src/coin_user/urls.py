from django.urls import path, include

from coin_user.views import SignUpView, ProfileView, VerifyEmailView

patterns = ([
    path('profile', ProfileView.as_view(), name='profile'),
    path('sign-up', SignUpView.as_view(), name='sign-up'),
    path('verify-email', VerifyEmailView.as_view(), name='verify-email'),
], 'user')

urlpatterns = [
    path('user/', include(patterns)),
]
