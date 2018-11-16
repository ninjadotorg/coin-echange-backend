from rest_framework import status
from rest_framework.exceptions import APIException


class InvalidVerificationException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid verification'
    default_code = 'invalid_verification'


class AlreadyVerifiedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Already verified'
    default_code = 'already_verified'


class NotReadyToVerifyException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Not ready to verify'
    default_code = 'not_ready_to_verify'
