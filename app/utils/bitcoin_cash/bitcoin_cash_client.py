#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from decimal import Decimal
from hashlib import sha256
from flask import current_app

from app.ext import redis_store
from app.utils.client import RPCClient
from app.utils import response_code

from app.utils.utils import *
from app.utils.enums.coin_type import CoinType


class BitcoinCashClient(object):
    ACCOUNT_DEPOSIT = 'deposit'
    ACCOUNT_HOT_WALLET = 'hot_wallet'

    def __init__(self, config=None, logger=None):
        if not config:
            config = current_app.config['CLIENT_AUTH']['bitcoin_cash']

        self.client = RPCClient(config, logger)

    def do_request(self, *args, **kwargs):
        return self.client.do_request(*args, **kwargs)

    def get_diff_base(self):
        return (2 ** 32)

    def get_unit_hashrate(self):
        return 1e12

    def get_fee(self, tx_inputs, tx_outputs, tx_fee_rate, max_fee=None):
        if not max_fee:
            max_fee = AppSetting.get_max_tx_fee(CoinType.BTC)
        fee = tx_fee_rate * (Decimal(148 * len(tx_inputs) +
                                     34 * (len(tx_outputs) + 1) + 10) / Decimal(1000))
        return Decimal(strfdecimal(min(fee, max_fee), 8))

    def get_estimate_fee(self, blocks=2):
        result = self.do_request('estimatefee', blocks)
        return result.data

    def get_balance(self):
        try:
            res = self.do_request('getbalance')
            balance = res.data
        except:
            current_app.logger.exception('bitcoin cash rpc get_balance fail')
            balance = 0
        return quantize(balance, 8)

    def get_network_hashrate(self):
        try:
            res = self.do_request('getnetworkhashps', 144)
            hashps = res.data
            redis_store.set('bitcoin_cash_network_hash_ps', hashps)
        except:
            hashps = redis_store.get('bitcoin_cash_network_hash_ps')
            hashps = float(hashps) if hashps else float(0)
            current_app.logger.exception(
                'bitcoin cash rcp get_network_hashrate fail, use cached value replace')
        return hashps

    def get_curr_difficulty(self):
        try:
            res = self.do_request('getdifficulty')
            diff = res.data
            redis_store.set('bitcoin_cash_curr_difficulty', diff)
        except:
            diff = redis_store.get('bitcoin_cash_curr_difficulty')
            diff = float(diff) if diff else float(0)
            current_app.logger.exception(
                'bitcoin cash rpc get_curr_difficulty fail, use cached value replace')
        return diff

    def get_block(self, block_hash):
        res = self.do_request('getblock', block_hash)
        return res.data

    def get_block_count(self):
        res = self.do_request('getblockcount')
        blockcount = res.data
        return blockcount

    def get_block_hash(self, height):
        res = self.do_request('getblockhash', height)
        return res.data

    def get_block_diff(self, height):
        block_hash = self.get_block_hash(height)
        block = self.get_block(block_hash)
        return quantize(block['difficulty'], 12)

    def get_block_reward(self, height):
        blockcount = height
        reward_base = 50.0
        half_interval = 210000
        while blockcount > half_interval:
            reward_base = reward_base / 2
            blockcount -= half_interval
        return reward_base

    def get_coinbase_reward(self, txid):
        r = self.get_raw_transaction(txid, True)
        if not r:
            return None
        amount = Decimal('0')
        for v in r['vout']:
            amount += Decimal(v['value'])
        return amount

    def get_new_address(self, account):
        result = self.do_request('getnewaddress', account)
        new_address = result.data
        return new_address

    def is_valid_address(self, address):
        try:
            result = self.do_request('validateaddress', address)
            return result.data['isvalid']
        except Exception as ex:
            current_app.logger.error(ex.message)

            def decode_base58(bc, length):
                digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
                n = 0
                for char in bc:
                    n = n * 58 + digits58.index(char)
                return ('%%0%dx' % (length << 1) % n).decode('hex')[-length:]

            bc_bytes = decode_base58(address, 25)
            return bc_bytes[-4:] == sha256(sha256(bc_bytes[:-4]).digest()).digest()[:4]

    def import_address(self, address, account, rescan=False):
        result = self.do_request('importaddress', address, account, rescan)
        return True

    def list_transactions(self, account, count, index):
        result = self.do_request('listtransactions', account, count, index)
        return result.data

    def get_transaction(self, tx):
        result = self.do_request('gettransaction', tx)
        return result.data

    def get_raw_transaction(self, tx, json_decode=True):
        result = self.do_request(
            'getrawtransaction', tx, (1 if json_decode else 0))
        return result.data

    def decode_raw_transaction(self, raw_tx):
        result = self.do_request('decoderawtransaction', raw_tx)
        return result.data

    def get_tx_fee(self, tx):
        total_input = 0
        for item in tx['vin']:
            try:
                info = self.do_request(
                    'getrawtransaction', item['txid'], 1).data
            except:
                return None
            try:
                total_input += int(info['vout'][item['vout']]['value'] * 1e8)
            except:
                return None
        total_output = 0
        for item in tx['vout']:
            try:
                total_output += int(item['value'] * 1e8)
            except:
                return None
        if total_input < total_output:
            return None
        return total_input - total_output

    def list_unspent(self, confirmations=1):
        result = self.do_request('listunspent', confirmations)
        return result.data

    def list_address_unspent(self, addresses, min_conf=0, max_conf=9999999):
        result = self.do_request('listunspent', min_conf, max_conf, addresses)
        return result.data

    def get_unspent_txs(self, accounts, confirmations=1):
        result = self.list_unspent(confirmations)
        available_balance = Decimal('0')
        available_txs = []
        for tx in result:
            if tx.get('account', '') in accounts:
                available_txs.append(tx)
                available_balance += Decimal(str(tx['amount']))
        current_app.logger.debug(
            '{accounts} available_balance:{available_balance}'.format(accounts=accounts, available_balance=str(available_balance)))
        return available_balance, available_txs

    def send_transaction(self, tx_inputs, tx_outputs):
        current_app.logger.info(
            'send_transaction tx_inputs:{tx_inputs}'.format(tx_inputs=tx_inputs))
        current_app.logger.info(
            'send_transaction tx_outputs:{tx_outputs}'.format(tx_outputs=tx_outputs))
        unsigned_tx_hex = self.do_request(
            'createrawtransaction', tx_inputs, tx_outputs).data
        signed_tx_hex = self.do_request(
            'signrawtransaction', unsigned_tx_hex).data['hex']
        tx_id = self.do_request('sendrawtransaction', signed_tx_hex).data
        return tx_id

    def send_raw_transaction(self, raw_tx):
        tx_id = self.do_request('sendrawtransaction', raw_tx).data
        return tx_id

    def publish_raw_transaction(self, raw_tx):
        '''
        return {'data': None, 'err_msg': None, 'err_no': 0}
        '''
        publish_tx_url = 'https://bch-chain.api.btc.com/v3/tools/tx-publish'
        r = requests.post(publish_tx_url, data={'rawhex': raw_tx}).json()
        return r

    def get_block_template(self):
        res = self.do_request('getblocktemplate')
        return res.data

    def speed_tx(self, txid):
        pass

    def verify_message(self, address, msg, signature):
        res = self.do_request('verifymessage', address, signature, msg)
        return res.data

    def dump_private_key(self, coin_address):
        res = self.do_request('dumpprivkey', coin_address)
        return res

    def import_private_key(self, private_key, account):
        res = self.do_request('importprivkey', private_key, account, False)
        return res

    def whc_decode_transaction(self, raw_tx):
        res = self.do_request('whc_decodetransaction', raw_tx)
        return res.data

    def whc_list_properties(self):
        res = self.do_request('whc_listproperties')
        return res.data

    def whc_get_balance(self, address, propertyid):
        res = self.do_request('whc_getbalance', address, propertyid)
        return res.data

    def whc_get_allbalances_for_address(self, address):
        res = self.do_request('whc_getallbalancesforaddress', address)
        return res.data

    def whc_get_property(self, propertyid):
        res = self.do_request('whc_getproperty', propertyid)
        return res.data

    def whc_get_transaction(self, txid):
        res = self.do_request('whc_gettransaction', txid)
        return res.data

    def whc_get_active_crowd(self, address):
        res = self.do_request('whc_getactivecrowd', address)
        return res.data

    def whc_get_allbalances_for_property(self, propertyid):
        res = self.do_request('whc_getallbalancesforid', propertyid)
        return res.data
