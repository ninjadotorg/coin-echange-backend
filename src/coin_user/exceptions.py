from rest_framework import status
from rest_framework.exceptions import APIException


class InvalidVerificationException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid verification'
    default_code = 'invalid_verification'


class NotYetVerifiedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Not yet verify previous level'
    default_code = 'not_yet_verify'


class AlreadyVerifiedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Already verified'
    default_code = 'already_verified'


class NotReadyToVerifyException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Not ready to verify'
    default_code = 'not_ready_to_verify'


class ExistedEmailException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Existed email'
    default_code = 'existed_email'


class ExistedNameException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Existed name'
    default_code = 'existed_name'


class ResetPasswordExpiredException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Reset password token expired'
    default_code = 'reset_password_expired'


class InvalidPasswordException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid password'
    default_code = 'invalid_password'
