from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets

from content.models import AboutUs, FAQ
from content.serializers import FAQSerializer, AboutUsSerializer


class AboutUsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AboutUs.objects.all()
    serializer_class = AboutUsSerializer
    filterset_fields = (
        'country',
    )

    @method_decorator(cache_page(5*60))
    def dispatch(self, *args, **kwargs):
        return super(AboutUsViewSet, self).dispatch(*args, **kwargs)


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FAQ.objects.filter(active=True).order_by('order', 'id')
    serializer_class = FAQSerializer
    filterset_fields = (
        'country',
    )

    @method_decorator(cache_page(5*60))
    def dispatch(self, *args, **kwargs):
        return super(FAQViewSet, self).dispatch(*args, **kwargs)
