import os
import re
import time
import uuid
import pytz
import json
import string
import decimal
import datetime
import hmac
import hashlib

from flask import current_app
from flask import request
from flask import url_for
from flask import g

from app.static_md5 import static_md5_map

def current_timestamp():
    return int(time.time())


def utcoffset():
    return time.timezone


def is_list(obj):
    return isinstance(obj, list)


def is_valid_password(password):
    if not re.match('^[\w$@$!%*#?&]{6,30}$', password):
        return False
    return True


def is_valid_coinbase_msg(msg):
    if not re.match('^[a-zA-Z0-9_,:!\.\?\+\-\s]{1,20}$', msg):
        return False
    return True


def is_valid_email(email):
    if not re.match('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return False
    if len(email) > 64:
        return False
    return True


def is_valid_country_code(country_code):
    if not re.match('^\d{1,4}$', country_code):
        return False
    return True


def is_supported_country_code(country_code):
    country_code = int(country_code)
    if country_code in country_code_white_list:
        return True
    return False


def is_valid_mobile(mobile):
    if not re.match('^\d{1,16}$', mobile):
        return False
    return True


def get_email_domain(email):
    return email.split('@')[1].strip()


def is_valid_payment_password(password):
    if not re.match('^\d{6}$', password):
        return False
    return True


def is_valid_ipv4(ip):
    if not re.match('^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}$', ip):
        return False
    return True


def mask_str(value, start=3, end=3, hidden_count=0):
    if not value:
        return value

    value_len = len(value)
    if not hidden_count:
        hidden_count = value_len - start - end

    if hidden_count < 1:
        return value
    return value[:start] + ('*' * hidden_count) + value[-end:]


def strftime(timestamp, f='%Y-%m-%d %H:%M:%S'):
    if timestamp <= 0:
        return ''
    if not hasattr(g, 'tz'):
        g.tz = pytz.timezone(current_app.config.get('TIMEZONE'))
    return datetime.datetime.fromtimestamp(timestamp, g.tz).strftime(f)


def time2datetime(t):
    return datetime.datetime.fromtimestamp(t, g.tz)


def datetime2time(d):
    return int(time.mktime(d.timetuple()))


def datestr2time(s, f='%Y-%m-%d'):
    if not s:
        return 0
    d = g.tz.localize(datetime.datetime.strptime(s, f))
    return datetime2time(d.astimezone(pytz.utc)) - time.timezone


def datestr2date(s, f='%Y-%m-%d'):
    t = datestr2time(s, f)
    return time2datetime(t)


def get_last_month(year, month):
    if month == 1:
        return datetime.date(year - 1, 12, 1)
    else:
        return datetime.date(year, month - 1, 1)


def get_next_month(year, month):
    if month == 12:
        return datetime.date(year + 1, 1, 1)
    else:
        return datetime.date(year, month + 1, 1)


def rstripzero(s):
    if '.' in s:
        s = s.rstrip('0')
        if s[-1] == '.':
            return s[:-1]
        return s
    return s


def strfdecimal(value, places=2):
    if value is None:
        value = decimal.Decimal(0)
    elif not isinstance(value, decimal.Decimal):
        value = decimal.Decimal(value)
    d = value.quantize(decimal.Decimal(10) ** -places,
                       rounding=decimal.ROUND_DOWN)
    s = '{0:f}'.format(d)
    return rstripzero(s)


def duration(seconds):
    hours = seconds / 3600
    seconds %= 3600
    minutes = seconds / 60
    seconds %= 60
    r = ''
    if hours:
        r += '%dh ' % hours
    if minutes:
        r += '%dm ' % minutes
    r += '%ds' % seconds
    return r


def quantize(value, places=2):
    if value is None:
        value = decimal.Decimal(0)
    elif not isinstance(value, decimal.Decimal):
        value = decimal.Decimal(value)
    return value.quantize(decimal.Decimal(10) ** -places, rounding=decimal.ROUND_DOWN)


def human_number(n):
    n = float(n)
    units = ['', 'K', 'M', 'G', 'T', 'P']
    for unit in units:
        if n < 1000:
            return '%.3f%s' % (n, unit)
        n /= 1000
    return '%.3f%s' % (n, 'E')


def human_int_number(n):
    n = float(n)
    units = ['', 'K', 'M', 'G', 'T', 'P']
    for unit in units:
        if n < 1000:
            return '%d %s' % (n, unit)
        n /= 1000
    return '%d %s' % (n, 'E')


def generate_token(random_string, length=32):
    return (hashlib.sha256(('%s%s' % (datetime.datetime.now(), random_string)).encode('utf-8')).hexdigest())[:length].upper()


def get_func_fullname(func):
    return '%s.%s' % (func.__module__, func.__qualname__)

def static_url(path, external=False, v=''):
    md5 = static_md5_map.get(path, '')
    if not md5:
        md5 = v
    return url_for('static', filename=path, _external=external) + '?v=' + md5

def register_blueprint(app, mod, url_prefix):
    handle_exceptions = app.handle_exception
    handle_user_exception = app.handle_user_exception
    app.register_blueprint(mod, url_prefix=url_prefix)
    app.handle_exception = handle_exceptions
    app.handle_user_exception = handle_user_exception

def coin_txid_url(coin, txid):
    url = ''
    coin = coin.upper()
    if g.testing:
        if coin == "BTC":
            url = "https://live.blockcypher.com/btc-testnet/tx/{txid}".format(
                txid=txid)
        elif coin == "BCH":
            url = "https://www.blocktrail.com/tBCC/tx/{txid}".format(txid=txid)
        elif coin == "BSV":
            url = "https://svblox.com/tx/{txid}".format(txid=txid)
        elif coin == "LTC":
            url = "https://live.blockcypher.com/ltc/tx/{txid}".format(
                txid=txid)
        elif coin == "DASH":
            url = "https://test.explorer.dash.org/tx/{txid}".format(txid=txid)
        elif coin == "ETH":
            url = "https://ropsten.etherscan.io/tx/{txid}".format(txid=txid)
        elif coin == "ETC":
            url = "http://gastracker.io/tx/{txid}".format(txid=txid)
        elif coin == "ZEC":
            url = "https://explorer.testnet.z.cash/tx/{txid}".format(txid=txid)
        elif coin == "NMC":
            url = "http://testnet.explorer.namecoin.info/tx/{txid}".format(
                txid=txid)
        elif coin == "DOGE":
            url = "https://live.blockcypher.com/doge/tx/{txid}".format(
                txid=txid)
    else:
        if coin == "BTC":
            url = "https://btc.com/{txid}".format(txid=txid)
        elif coin == "BCH":
            url = "https://bch.btc.com/{txid}".format(txid=txid)
        elif coin == "BSV":
            url = "https://svblox.com/tx/{txid}".format(txid=txid)
        elif coin == "LTC":
            url = "https://chainz.cryptoid.info/ltc/tx.dws?{txid}.htm".format(
                txid=txid)
        elif coin == "DASH":
            url = "https://chainz.cryptoid.info/dash/tx.dws?{txid}.htm".format(
                txid=txid)
        elif coin == "ETH":
            url = "https://etherscan.io/tx/{txid}".format(txid=txid)
        elif coin == "ETC":
            url = "http://gastracker.io/tx/{txid}".format(txid=txid)
        elif coin == "ZEC":
            url = "https://explorer.zcha.in/transactions/{txid}".format(
                txid=txid)
        elif coin == "NMC":
            url = "http://namecha.in/tx/{txid}".format(txid=txid)
        elif coin == "DOGE":
            url = "https://live.blockcypher.com/doge/tx/{txid}".format(
                txid=txid)
    return url


def coin_address_url(coin, address):
    url = ''
    coin = coin.upper()
    if g.testing:
        if coin == "BTC":
            url = "https://live.blockcypher.com/btc-testnet/address/{address}".format(
                address=address)
        elif coin == "BCH":
            url = "https://www.blocktrail.com/tBCC/address/{address}".format(
                address=address)
        elif coin == "BSV":
            url = "https://svblox.com/address/{address}".format(
                address=address)
        elif coin == "LTC":
            url = "https://live.blockcypher.com/ltc/address/{address}".format(
                address=address)
        elif coin == "DASH":
            url = "https://test.explorer.dash.org/address/{address}".format(
                address=address)
        elif coin == "ETH":
            url = "https://ropsten.etherscan.io/address/{address}".format(
                address=address)
        elif coin == "ETC":
            url = "http://gastracker.io/addr/{address}".format(address=address)
        elif coin == "ZEC":
            url = "https://explorer.testnet.z.cash/address/{address}".format(
                address=address)
        elif coin == "NMC":
            url = "http://testnet.explorer.namecoin.info/a/{address}".format(
                address=address)
        elif coin == "DOGE":
            url = "https://live.blockcypher.com/doge/address/{address}".format(
                address=address)
    else:
        if coin == "BTC":
            url = "https://btc.com/{address}".format(address=address)
        elif coin == "BCH":
            url = "https://bch.btc.com/{address}".format(
                address=address)
        elif coin == "BSV":
            url = "https://svblox.com/address/{address}".format(
                address=address)
        elif coin == "LTC":
            url = "https://chainz.cryptoid.info/ltc/address.dws?{address}.htm".format(
                address=address)
        elif coin == "DASH":
            url = "https://chainz.cryptoid.info/dash/address.dws?{address}.htm".format(
                address=address)
        elif coin == "ETH":
            url = "https://etherscan.io/address/{address}".format(
                address=address)
        elif coin == "ETC":
            url = "http://gastracker.io/addr/{address}".format(address=address)
        elif coin == "ZEC":
            url = "https://explorer.zcha.in/accounts/{address}".format(
                address=address)
        elif coin == "NMC":
            url = "http://namecha.in/address/{address}".format(address=address)
        elif coin == "DOGE":
            url = "https://live.blockcypher.com/doge/address/{address}".format(
                address=address)
    return url


def coin_block_hash_url(coin, block_hash, block_type='main'):
    url = ''
    coin = coin.upper()
    if g.testing:
        if coin == "BTC":
            url = "https://live.blockcypher.com/btc-testnet/block_hash/{block_hash}".format(
                block_hash=block_hash)
        elif coin == "BCH":
            url = "https://www.blocktrail.com/tBCC/block/{block_hash}".format(
                block_hash=block_hash)
        elif coin == "BSV":
            url = "https://svblox.com/block/{block_hash}".format(
                block_hash=block_hash)
        elif coin == "LTC":
            url = "https://live.blockcypher.com/ltc/block/{block_hash}".format(
                block_hash=block_hash)
        elif coin == "DASH":
            url = "https://test.explorer.dash.org/block/{block_hash}".format(
                block_hash=block_hash)
        elif coin == "ETH":
            if block_type == 'uncle':
                url = "https://ropsten.etherscan.io/uncle/{block_hash}".format(
                    block_hash=block_hash)
            else:
                url = "https://ropsten.etherscan.io/block/{block_hash}".format(
                    block_hash=block_hash)
        elif coin == "ETC":
            if block_type == 'uncle':
                url = "http://gastracker.io/uncle/{block_hash}".format(
                    block_hash=block_hash)
            else:
                url = "http://gastracker.io/block/{block_hash}".format(
                    block_hash=block_hash)
        elif coin == "ZEC":
            url = "https://explorer.testnet.z.cash/block/{block_hash}".format(
                block_hash=block_hash)
        elif coin == "NMC":
            url = "http://testnet.explorer.namecoin.info/a/{block_hash}".format(
                block_hash=block_hash)
        elif coin == "DOGE":
            url = "https://live.blockcypher.com/doge/block/{block_hash}".format(
                block_hash=block_hash)
    else:
        if coin == "BTC":
            url = "https://btc.com/{block_hash}".format(block_hash=block_hash)
        elif coin == "BCH":
            url = "https://bch.btc.com/{block_hash}".format(
                block_hash=block_hash)
        elif coin == "BSV":
            url = "https://svblox.com/block/{block_hash}".format(
                block_hash=block_hash)
        elif coin == "LTC":
            url = "https://chainz.cryptoid.info/ltc/block.dws?{block_hash}.htm".format(
                block_hash=block_hash)
        elif coin == "DASH":
            url = "https://chainz.cryptoid.info/dash/block.dws?{block_hash}.htm".format(
                block_hash=block_hash)
        elif coin == "ETH":
            if block_type == 'uncle':
                url = "https://etherscan.io/uncle/{block_hash}".format(
                    block_hash=block_hash)
            else:
                url = "https://etherscan.io/block/{block_hash}".format(
                    block_hash=block_hash)
        elif coin == "ETC":
            if block_type == 'uncle':
                url = "http://gastracker.io/uncle/{block_hash}".format(
                    block_hash=block_hash)
            else:
                url = "http://gastracker.io/block/{block_hash}".format(
                    block_hash=block_hash)
        elif coin == "ZEC":
            url = "https://explorer.zcha.in/blocks/{block_hash}".format(
                block_hash=block_hash)
        elif coin == "NMC":
            url = "http://namecha.in/block/{block_hash}".format(
                block_hash=block_hash)
        elif coin == "DOGE":
            url = "https://live.blockcypher.com/doge/block/{block_hash}".format(
                block_hash=block_hash)
    return url
