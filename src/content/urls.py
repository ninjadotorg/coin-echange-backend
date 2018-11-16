from django.urls import path, include
from rest_framework.routers import DefaultRouter

from content.resource import AboutUsViewSet, FAQViewSet

router = DefaultRouter()
router.register('about-us', AboutUsViewSet)
router.register('faq', FAQViewSet)

patterns = ([
    path('', include(router.urls)),
], 'content')

urlpatterns = [
    path('content/', include(patterns)),
]
