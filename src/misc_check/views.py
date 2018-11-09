from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.exceptions import UnexpectedException


class ProtectedView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }

        return Response(content)


class PublicView(APIView):
    def get(self, request, format=None):
        if str(request.user) == 'AnonymousUser':
            raise UnexpectedException
