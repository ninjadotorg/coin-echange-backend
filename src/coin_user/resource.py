from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from coin_user.models import Contact
from coin_user.serializers import ContactSerializer


class ContactViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, )
    serializer_class = ContactSerializer
    queryset = Contact.objects.none()

    def get_queryset(self):
        return Contact.objects.filter(user__user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        exchange_user = self.request.user.exchange_user
        serializer.save(user=exchange_user)

    def perform_update(self, serializer):
        exchange_user = self.request.user.exchange_user
        serializer.save(user=exchange_user)
