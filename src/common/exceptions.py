from rest_framework import status
from rest_framework.exceptions import APIException


class UnexpectedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Unexpected error'
    default_code = 'unexpected_error'


class InvalidDataException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid data'
    default_code = 'invalid_data'


class InvalidInputDataException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid input data'
    default_code = 'invalid_input_data'


class InvalidAddress(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid address'
    default_code = 'invalid_address'
