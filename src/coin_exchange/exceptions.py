from rest_framework import status
from rest_framework.exceptions import APIException


class CoinOrderStatusInvalidException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Coin order status invalid'
    default_code = 'coin_order_status_invalid'


class CoinOverLimitException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Coin over limit'
    default_code = 'coin_over_limit'
