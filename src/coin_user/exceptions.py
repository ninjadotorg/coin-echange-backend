from rest_framework import status
from rest_framework.exceptions import APIException


class InvalidVerificationException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid verification'
    default_code = 'invalid_verification'
