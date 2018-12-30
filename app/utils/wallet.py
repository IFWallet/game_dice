import decimal
import random

from cashaddress import convert
from flask import current_app
from sqlalchemy.sql import func
from sqlalchemy.orm import subqueryload

from app.ext import db
from app.ext import cache

from app.models import DiceOrder

from app.utils import utils
from app.utils.bitcoin_cash import BitcoinCashClient
from app.utils.enums.coin_type import CoinType
from app.utils.rpc import get_rpc_client
from app.utils.utils import current_timestamp


def get_random_hot_wallet_address(coin):
    return current_app.config['CHOICE_ADDRESSES'][coin][2]

def get_tx_outputs(coin, tx_outputs, send_amount):
    minimal_tx_fee = decimal.Decimal('0.000005')
    rest_amount = send_amount
    while rest_amount > minimal_tx_fee:
        receive_addr = get_random_hot_wallet_address(coin)
        tx_outputs.setdefault(receive_addr, 0)
        tx_outputs[receive_addr] = float(
            tx_outputs[receive_addr]) + float(rest_amount)
        rest_amount = 0

    return tx_outputs, rest_amount

def is_deposit_tx_exist(coin, txid, vout):
    record = DiceOrder.query.filter(DiceOrder.coin == coin).\
        filter(DiceOrder.tx == txid).\
        filter(DiceOrder.vout == vout).first()
    return True if record else False


def is_tx_too_old(tx):
    if tx['timereceived'] < (current_timestamp() - 3 * 86400):
        return True
    return False

def get_deposit_unprocess_txs(coin, account):
    unprocess_txs = []
    index = 0
    count = 100
    rpc_client = get_rpc_client(coin)
    while True:
        finish = False
        r = rpc_client.list_transactions(account, count, index)
        if not r:
            break
        for tx in r[::-1]:
            if tx['category'] == 'receive':
                if is_deposit_tx_exist(coin, tx['txid'], tx['vout']) or is_tx_too_old(tx):
                    finish = True
                    break
                unprocess_txs.append(tx)
        if finish:
            break
        if len(r) < count:
            break
        index += len(r)
    return unprocess_txs[::-1]
