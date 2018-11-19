from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from content.models import AboutUs, FAQ
from content.serializers import FAQSerializer, AboutUsSerializer


class AboutUsViewSet(mixins.RetrieveModelMixin,
                     GenericViewSet):
    queryset = AboutUs.objects.all()
    serializer_class = AboutUsSerializer

    @method_decorator(cache_page(5 * 60))
    def dispatch(self, *args, **kwargs):
        return super(AboutUsViewSet, self).dispatch(*args, **kwargs)


class FAQViewSet(mixins.ListModelMixin,
                 GenericViewSet):
    queryset = FAQ.objects.filter(active=True).order_by('order', 'id')
    serializer_class = FAQSerializer
    filterset_fields = (
        'language',
    )

    @method_decorator(cache_page(5 * 60))
    def dispatch(self, *args, **kwargs):
        return super(FAQViewSet, self).dispatch(*args, **kwargs)
