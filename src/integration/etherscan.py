from decimal import Decimal

import requests
from django.conf import settings

from common.decorators import raise_api_exception
from integration.exceptions import ExternalAPIException
from integration.objects import AddressResponse, TransactionResponse, ETHTransactionResponse

WEI = Decimal('1000000000000000000')


@raise_api_exception(ExternalAPIException)
def make_request(uri: str, params=None):
    resp = requests.get(settings.ETHERSCAN['URL'] + '?' + uri + '&apikey={}'.format(settings.ETHERSCAN['API_KEY']),
                        headers={
                            'Accept': 'application/json'
                        })
    if not resp.ok:
        raise Exception('Etherscan: StatusCode={} Detail={}'.format(resp.status_code, resp.content))

    return resp


def get_address(address: str) -> AddressResponse:
    resp = make_request('module=account&action=txlist&address={}&sort=asc'.format(address))
    data = resp.json()
    addr_obj = AddressResponse(address,
                               None,
                               tx_hashes=list(map(lambda item: item['hash'], data['result'])),
                               unconfirmed_balance=None,
                               unconfirmed_tx=None)

    return addr_obj


def get_eth_transaction(tx_hash: str):
    resp = make_request('module=proxy&action=eth_getTransactionByHash&txhash={}'.format(tx_hash))
    data = resp.json()['result']

    return data


def get_eth_transaction_receipt(tx_hash: str):
    resp = make_request('module=proxy&action=eth_getTransactionReceipt&txhash={}'.format(tx_hash))
    data = resp.json()['result']

    return data


def get_transaction(tx_hash: str) -> TransactionResponse:
    tx_data = get_eth_transaction(tx_hash)
    tx_receipt_data = get_eth_transaction_receipt(tx_hash)

    value = Decimal(str(int(tx_data['value'], 16))) / WEI
    gas = Decimal(str(int(tx_data['gas'], 16)))
    block_number = int(tx_data['blockNumber'], 16)
    gas_used = Decimal(str(int(tx_receipt_data['cumulativeGasUsed'], 16)))

    is_success = False
    is_pending = False if block_number else False
    if not is_pending:
        is_success = gas < gas_used

    return ETHTransactionResponse(tx_hash, value, is_pending=is_pending, is_success=is_success)
