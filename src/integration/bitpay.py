from common.decorators import raise_api_exception
from integration.exceptions import ExternalAPIException


@raise_api_exception(ExternalAPIException)
def get_btc_address(address: str):
    pass
