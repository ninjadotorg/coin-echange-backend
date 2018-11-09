from django.urls import path, include

patterns = ([
], 'exchange')

urlpatterns = [
    path('exchange/', include(patterns)),
]
