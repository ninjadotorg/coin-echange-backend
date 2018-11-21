from decimal import Decimal

import requests
from django.conf import settings

from common.decorators import raise_api_exception
from integration.exceptions import ExternalAPIException
from integration.objects import AddressResponse, TransactionResponse


@raise_api_exception(ExternalAPIException)
def make_bitpay_btc_request(uri: str, params=None):
    resp = requests.get(settings.BITPAY_BTC['URL'] + uri, headers={
        'Accept': 'application/json'
    })
    if not resp.ok:
        raise Exception('BitPay: StatusCode={} Detail={}'.format(resp.status_code, resp.content))

    return resp


def get_btc_address(address: str) -> AddressResponse:
    resp = make_bitpay_btc_request('/addr/{}'.format(address))
    data = resp.json()
    addr_obj = AddressResponse(data['addrStr'],
                               Decimal(str(data['balance'])),
                               tx_hashes=data['transactions'],
                               unconfirmed_balance=Decimal(str(data['unconfirmedBalance'])),
                               unconfirmed_tx=data['unconfirmedTxApperances'])

    return addr_obj


def get_btc_transaction(tx_hash: str) -> TransactionResponse:
    resp = make_bitpay_btc_request('/tx/{}'.format(tx_hash))
    data = resp.json()
    tx_obj = TransactionResponse(data['txid'],
                                 data['valueOut'],
                                 data['confirmations'])

    return tx_obj
