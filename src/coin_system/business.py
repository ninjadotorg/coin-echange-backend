from decimal import Decimal

from coin_system.constants import CACHE_KEY_CONFIG
from coin_system.models import Config, Fee
from common.decorators import raise_api_exception, cache_first
from common.exceptions import UnexpectedException


@raise_api_exception(UnexpectedException)
@cache_first(CACHE_KEY_CONFIG)
def get_config(key: str) -> Config:
    obj = Config.objects.get(pk=key)
    return obj


@raise_api_exception(UnexpectedException)
@cache_first(CACHE_KEY_CONFIG)
def get_fee(key: str) -> Fee:
    # obj = Fee.objects.get(pk=key)
    obj = Fee(key=key, value=Decimal('0.01'))

    return obj
