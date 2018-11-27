from django.shortcuts import get_object_or_404
from rest_framework import generics

from common.constants import LANGUAGE
from content.models import StaticPage
from content.serializers import StaticPageSerializer


class StaticPageView(generics.RetrieveAPIView):
    queryset = StaticPage.objects.all()
    serializer_class = StaticPageSerializer

    def get_object(self):
        queryset = self.get_queryset()
        language = self.request.query_params.get('language', LANGUAGE.en)
        page = self.request.query_params.get('page', '')

        obj = get_object_or_404(queryset, page=page, language=language)

        return obj
