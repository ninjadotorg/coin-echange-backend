from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError


class UnexpectedException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Unexpected error'
    default_code = 'unexpected_error'


class InvalidDataException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid data'
    default_code = 'invalid_data'
