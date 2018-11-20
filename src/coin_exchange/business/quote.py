import logging
from decimal import Decimal

from rest_framework.exceptions import NotAuthenticated, ValidationError

from coin_exchange.constants import FEE_COIN_ORDER_COD, FEE_COIN_ORDER_BANK, FEE_COIN_SELLING_ORDER_BANK, ORDER_TYPE
from coin_exchange.exceptions import CoinUserOverLimitException, CoinOverLimitException
from coin_exchange.models import UserLimit, Pool
from coin_exchange.serializers import QuoteSerializer, QuoteInputSerializer, QuoteReverseInputSerializer, \
    QuoteReverseSerializer
from coin_system.business import markup_fee, round_currency, remove_markup_fee
from common.business import PriceManagement, RateManagement
from common.constants import FIAT_CURRENCY, DIRECTION, DIRECTION_ALL
from common.exceptions import InvalidDataException


class QuoteManagement(object):
    @staticmethod
    def get_quote(user, params) -> QuoteSerializer:
        input_serializer = QuoteInputSerializer(data={
            'amount': params.get('amount'),
            'currency': params.get('currency'),
            'fiat_currency': params.get('fiat_currency', FIAT_CURRENCY.USD),
            'pool_check': params.get('check', False),
            'user_check': params.get('user_check', False),
            'direction': params.get('direction', DIRECTION.buy),
        })

        if input_serializer.is_valid(raise_exception=True):
            safe_data = input_serializer.validated_data
            direction = safe_data['direction']

            amount = safe_data['amount']
            price = QuoteManagement.get_price(direction, safe_data)

            raw_fiat_amount = amount * price
            fiat_local_currency = safe_data['fiat_currency']
            raw_fiat_local_amount = RateManagement.convert_to_local_currency(raw_fiat_amount, fiat_local_currency)

            QuoteManagement.check_user_limit(user, raw_fiat_local_amount, safe_data)
            QuoteManagement.check_pool(direction, amount, safe_data)

            if direction == DIRECTION.buy:
                fiat_amount, fiat_amount_fee = markup_fee(raw_fiat_amount, FEE_COIN_ORDER_BANK)
            else:
                fiat_amount, fiat_amount_fee = markup_fee(raw_fiat_amount, FEE_COIN_SELLING_ORDER_BANK)

            fiat_local_amount = RateManagement.convert_to_local_currency(fiat_amount, fiat_local_currency)
            fee_local = RateManagement.convert_to_local_currency(fiat_amount_fee, fiat_local_currency)

            if direction == DIRECTION.buy:
                fiat_amount_cod, fiat_amount_fee_cod = markup_fee(price, FEE_COIN_ORDER_COD)
                fiat_local_amount_cod = RateManagement.convert_to_local_currency(fiat_amount_cod, fiat_local_currency)
                fee_local_cod = RateManagement.convert_to_local_currency(fiat_amount_fee_cod, fiat_local_currency)
            else:
                fiat_amount_cod = fiat_amount_fee_cod = Decimal(0)
                fiat_local_amount_cod = fee_local_cod = Decimal(0)

            serializer = QuoteSerializer(data={
                'fiat_amount': round_currency(fiat_amount),
                'fiat_currency': FIAT_CURRENCY.USD,
                'fiat_local_amount': round_currency(fiat_local_amount),
                'fiat_local_currency': fiat_local_currency,
                'fiat_amount_cod': round_currency(fiat_amount_cod),
                'fiat_local_amount_cod': round_currency(fiat_local_amount_cod),
                'fee': round_currency(fiat_amount_fee),
                'fee_cod': round_currency(fiat_amount_fee_cod),
                'fee_local': round_currency(fee_local),
                'fee_local_cod': round_currency(fee_local_cod),
                'raw_fiat_amount': round_currency(raw_fiat_amount),
                'price': round_currency(price),
                'amount': amount,
                'currency': safe_data['currency'],
                'direction': safe_data['direction']
            })
            serializer.is_valid(raise_exception=True)

            return serializer

    @staticmethod
    def get_quote_reverse(user, params) -> QuoteReverseSerializer:
        input_serializer = QuoteReverseInputSerializer(data={
            'fiat_amount': params.get('fiat_amount'),
            'currency': params.get('currency'),
            'fiat_currency': params.get('fiat_currency', FIAT_CURRENCY.USD),
            'pool_check': params.get('check', False),
            'user_check': params.get('user_check', False),
            'direction': params.get('direction', DIRECTION.buy),
            'order_type': params.get('type', ORDER_TYPE.bank)
        })

        order_type = input_serializer.initial_data['order_type']
        if order_type not in ORDER_TYPE:
            raise ValidationError

        if input_serializer.is_valid(raise_exception=True):
            safe_data = input_serializer.validated_data
            direction = safe_data['direction']

            fiat_local_amount = safe_data['fiat_amount']
            fiat_local_currency = safe_data['fiat_currency']
            fiat_amount = RateManagement.convert_from_local_currency(fiat_local_amount, fiat_local_currency)

            if direction == DIRECTION.buy:
                raw_fiat_amount, fiat_amount_fee = remove_markup_fee(fiat_amount, FEE_COIN_ORDER_BANK)
            else:
                raw_fiat_amount, fiat_amount_fee = remove_markup_fee(fiat_amount, FEE_COIN_SELLING_ORDER_BANK)

            raw_fiat_local_amount = RateManagement.convert_to_local_currency(raw_fiat_amount, fiat_local_currency)
            price = QuoteManagement.get_price(direction, safe_data)
            amount = raw_fiat_amount / price

            QuoteManagement.check_user_limit(user, raw_fiat_local_amount, safe_data)
            QuoteManagement.check_pool(direction, amount, safe_data)

            fiat_local_amount = RateManagement.convert_to_local_currency(fiat_amount, fiat_local_currency)

            serializer = QuoteReverseSerializer(data={
                'fiat_amount': round_currency(fiat_amount),
                'fiat_currency': FIAT_CURRENCY.USD,
                'fiat_local_amount': round_currency(fiat_local_amount),
                'fiat_local_currency': fiat_local_currency,
                'raw_fiat_amount': round_currency(raw_fiat_amount),
                'price': round_currency(price),
                'amount': amount,
                'currency': safe_data['currency'],
                'direction': safe_data['direction']
            })
            serializer.is_valid(raise_exception=True)

            return serializer

    @staticmethod
    def get_price(direction, safe_data):
        price_obj = PriceManagement.get_cache_price(safe_data['currency'])
        if direction == DIRECTION.buy:
            price = price_obj.buy
        else:
            price = price_obj.sell
        return price

    @staticmethod
    def check_pool(direction, amount, safe_data):
        if safe_data['pool_check']:
            pool = Pool.objects.get(direction=direction,
                                    currency=safe_data['currency'])
            if pool.usage + amount > pool.limit:
                raise CoinOverLimitException

    @staticmethod
    def check_user_limit(user, local_price, safe_data):
        if safe_data['user_check']:
            # request.user
            # User logged in
            if user and user.is_authenticated:
                # Get user limit to check
                try:
                    user_limit = UserLimit.objects.get(user__user=user, direction=DIRECTION_ALL,
                                                       fiat_currency=safe_data['fiat_currency'])
                    if user_limit.usage + local_price > user_limit.limit:
                        raise CoinUserOverLimitException
                except UserLimit.DoesNotExist as e:
                    logging.exception(e)
                    raise InvalidDataException
            else:
                raise NotAuthenticated
