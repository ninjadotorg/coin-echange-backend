from django.urls import path, include

from coin_user.views import SignUpView, ProfileView

patterns = ([
    path('profile', ProfileView.as_view(), name='profile'),
    path('sign-up', SignUpView.as_view(), name='sign-up'),
], 'user')

urlpatterns = [
    path('user/', include(patterns)),
]
