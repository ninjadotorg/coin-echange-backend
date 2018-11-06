from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.exceptions import UnexpectedException
from common.http import SuccessResponse


class ProtectedView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }

        return SuccessResponse(content)


class PublicView(APIView):
    def get(self, request, format=None):
        if str(request.user) == 'AnonymousUser':
            raise UnexpectedException
