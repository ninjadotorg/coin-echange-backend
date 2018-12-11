from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from coin_user.models import Contact, ExchangeUserLog
from coin_user.serializers import ContactSerializer, ExchangeUserLogSerializer
from common.http import StandardPagination


class ContactViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ContactSerializer
    pagination_class = StandardPagination
    queryset = Contact.objects.none()

    def get_queryset(self):
        return Contact.objects.filter(user__user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        exchange_user = self.request.user.exchange_user
        serializer.save(user=exchange_user)

    def perform_update(self, serializer):
        exchange_user = self.request.user.exchange_user
        serializer.save(user=exchange_user)


class ExchangeUserLogViewSet(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ExchangeUserLogSerializer
    queryset = ExchangeUserLog.objects.none()

    def get_queryset(self):
        return ExchangeUserLog.objects.filter(user__user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        exchange_user = self.request.user.exchange_user
        serializer.save(user=exchange_user)
