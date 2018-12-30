#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import current_app
from app.utils.bitcoin_cash import BitcoinCashClient
from app.utils.enums.coin_type import CoinType


def get_rpc_client(coin):
    rpc_cli = None
    client_config = 'CLIENT_AUTH'

    if coin == CoinType.BCH:
        rpc_cli = BitcoinCashClient(
            current_app.config[client_config]['bitcoin_cash'])
    elif coin == CoinType.BSV:
        rpc_cli = BitcoinCashClient(
            current_app.config[client_config]['bitcoin_sv'])
    else:
        raise NotImplementedError
    return rpc_cli


