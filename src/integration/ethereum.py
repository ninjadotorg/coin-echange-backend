import time
from decimal import Decimal

import simplejson

from django.conf import settings
from web3 import Web3

from common.decorators import raise_api_exception
from integration.exceptions import ExternalAPIException

w3 = Web3(Web3.HTTPProvider(settings.ETH['URL']))


# Test contract address: 0xc25D80fF9D25802cb69b2A751394F83534011308
ERC20_ABI = simplejson.loads('[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":true,"name":"_to","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},{"indexed":true,"name":"_spender","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Approval","type":"event"}]')  # noqa: 501


@raise_api_exception(ExternalAPIException)
def check_connected():
    return w3.isConnected()


@raise_api_exception(ExternalAPIException)
def get_erc20(address: str):
    return w3.eth.contract(address=Web3.toChecksumAddress(address), abi=ERC20_ABI)


@raise_api_exception(ExternalAPIException)
def inspect_erc20(address: str):
    checksum_addr = Web3.toChecksumAddress(address)
    erc20 = get_erc20(address)

    decimals = erc20.functions.decimals().call()

    return {
        'address': checksum_addr,
        'name': erc20.functions.name().call(),
        'symbol': erc20.functions.symbol().call(),
        'decimals': erc20.functions.decimals().call(),
        'total_supply': Decimal(erc20.functions.totalSupply().call()) / Decimal(10 ** decimals),
    }


@raise_api_exception(ExternalAPIException)
def send_ether_to_contract(amount, contract_address):
    amount_in_wei = w3.toWei(amount, 'ether')

    nonce = w3.eth.getTransactionCount(settings.ETH['WALLET'])
    txn_dict = {
            'to': contract_address,
            'value': amount_in_wei,
            'gas': 2000000,
            'gasPrice': w3.eth.gasPrice,
            'nonce': nonce,
            'chainId': 4 if settings.TEST else 1
    }
    signed_txn = w3.eth.account.signTransaction(txn_dict, settings.ETH['WALLET_KEY'])
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    txn_receipt = None
    count = 0
    while txn_receipt is None and (count < 30):
        txn_receipt = w3.eth.getTransactionReceipt(txn_hash)
        time.sleep(10)

    if txn_receipt is None:
        return {'status': 'failed', 'error': 'timeout'}

    return {'status': 'added', 'txn_receipt': txn_receipt}


@raise_api_exception(ExternalAPIException)
def transfer(contract: str, decimals: int, to_address: str, amount: Decimal):
    from_address = settings.ETH['WALLET']
    nonce = w3.eth.getTransactionCount(from_address)
    erc20 = get_erc20(contract)
    unsigned_transaction = erc20.functions.transfer(
        Web3.toChecksumAddress(to_address),
        int(amount * Decimal(10 ** decimals))
    ).buildTransaction({
        'chainId': 4 if settings.TEST else 1,
        'gas': 100000,
        'gasPrice': w3.eth.gasPrice,
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.signTransaction(unsigned_transaction, settings.ETH['WALLET_KEY'])
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    txn_receipt = None
    count = 0
    while txn_receipt is None and (count < 30):
        txn_receipt = w3.eth.getTransactionReceipt(txn_hash)
        print('waiting')
        time.sleep(10)

    if txn_receipt is None:
        return {'status': 'failed', 'error': 'timeout'}

    return {'status': 'added', 'txn_receipt': txn_receipt}
