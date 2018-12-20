from coin_exchange.constants import CACHE_KEY_TOKEN
from coin_exchange.models import CryptoToken
from common.decorators import cache_first


class TokenManagement(object):
    @staticmethod
    @cache_first(CACHE_KEY_TOKEN, timeout=5 * 60)
    def list_token() -> CryptoToken:
        obj = CryptoToken.objects.filter(active=True)
        return obj
