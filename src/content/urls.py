from django.urls import path, include
from rest_framework.routers import DefaultRouter

from content.resource import FAQViewSet
from content.views import StaticPageView

router = DefaultRouter()
router.register('faq', FAQViewSet)

patterns = ([
    path('', include(router.urls)),
    path('static-page/', StaticPageView.as_view(), name='static-page-view')
], 'content')

urlpatterns = [
    path('content/', include(patterns)),
]
