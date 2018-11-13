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


class CoinUserOverLimitException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Coin user over limit'
    default_code = 'coin_user_over_limit'


class AmountIsTooSmallException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Amount is too small'
    default_code = 'amount_is_too_small'


class PriceChangeException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Price changed'
    default_code = 'price_changed'
