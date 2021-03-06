from decimal import Decimal, ROUND_CEILING

from coin_system.constants import CACHE_KEY_CONFIG, CACHE_KEY_FEE, CACHE_KEY_COUNTRY_DEFAULT, FEE_TYPE
from coin_system.models import Config, Fee, CountryDefaultConfig
from common.decorators import raise_api_exception, cache_first
from common.exceptions import UnexpectedException, InvalidDataException


@raise_api_exception(UnexpectedException)
@cache_first(CACHE_KEY_CONFIG, timeout=5*60)
def get_config(key: str) -> Config:
    obj = Config.objects.get(pk=key)
    return obj


@raise_api_exception(UnexpectedException)
@cache_first(CACHE_KEY_FEE, timeout=5*60)
def get_fee(key: str) -> Fee:
    obj = Fee.objects.get(pk=key)
    return obj


@raise_api_exception(UnexpectedException)
@cache_first(CACHE_KEY_COUNTRY_DEFAULT, timeout=5*60)
def get_country_default(key: str) -> CountryDefaultConfig:
    obj = CountryDefaultConfig.objects.get(pk=key)
    return obj


def markup_fee(amount: Decimal, fee_key: str) -> (Decimal, Decimal):
    fee = get_fee(fee_key)
    value = fee.value
    if fee.fee_type == FEE_TYPE.fixed:
        return amount + value, value
    elif fee.fee_type == FEE_TYPE.percentage:
        added_fee = (amount * value) / Decimal('100')
        return amount + added_fee, added_fee

    raise InvalidDataException


def remove_markup_fee(amount: Decimal, fee_key: str) -> (Decimal, Decimal):
    fee = get_fee(fee_key)
    value = fee.value
    if fee.fee_type == FEE_TYPE.fixed:
        return amount - value, value
    elif fee.fee_type == FEE_TYPE.percentage:
        removed_fee = amount / (Decimal(1) + value / Decimal('100'))
        return removed_fee, amount - removed_fee

    raise InvalidDataException


def round_currency(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal('.01'), ROUND_CEILING)


def round_crypto_currency(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal('.000001'), ROUND_CEILING)
