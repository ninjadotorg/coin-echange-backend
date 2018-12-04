from rest_framework.response import Response
from rest_framework.views import APIView

from notification.business import OrderNotification, UserVerificationNotification


class NewOrderNotificationView(APIView):
    def post(self, request, format=None):
        print(request.data)
        OrderNotification.send_new_order_notification(request.data)
        return Response()


class UserVerificationNotificationView(APIView):
    def post(self, request, format=None):
        UserVerificationNotification.send_user_verification_notification(request.data)
        return Response()
