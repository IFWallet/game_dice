from flask import current_app, g
from app.ext import db
from app.ext import celery

from app.models import DiceOrder

from app.utils.rpc import get_rpc_client
from app.utils.utils import quantize
from app.utils.utils import current_timestamp
from app.utils.wallet import get_deposit_unprocess_txs
from app.utils.enums.coin_type import CoinType

from app.decorators.process import LockProcessDeco

coin = CoinType.BCH


@celery.task
@LockProcessDeco(is_wait=False)
def process_bch_deposit_task():
    txs = get_deposit_unprocess_txs(coin, 'game_dice')
    rpc_client = get_rpc_client(coin)
    block_height = rpc_client.get_block_count()
    even_address = current_app.config['CHOICE_ADDRESSES'][coin][0]
    odd_address = current_app.config['CHOICE_ADDRESSES'][coin][1]
    print(block_height, even_address, odd_address)

    for tx in txs:
        print(tx['address'])
        if tx['address'] not in [even_address, odd_address]:
            continue

        try:
            tx_obj = rpc_client.get_raw_transaction(tx['txid'])
            print(tx_obj['vin'][0]['txid'], tx_obj['vin'][0]['vout'])
            input_tx_obj = rpc_client.get_raw_transaction(tx_obj['vin'][0]['txid'])
            from_vout = tx_obj['vin'][0]['vout']
            from_address = input_tx_obj['vout'][from_vout]['scriptPubKey']['addresses'][0]
            print('from_address', from_address)
        except:
            current_app.logger.error("process_bch_deposit_task fail: %s, %s", coin, tx['txid'])
            continue

        order = DiceOrder()
        order.coin = coin
        order.game_round = block_height + 1

        order.from_address = from_address
        order.address = tx['address']
        order.tx = tx['txid']
        order.vout = tx['vout']
        order.amount = tx['amount']
        order.choice = 0 if tx['address'] == even_address else 1
        print(order.choice, tx['address'])
        order.confirmations = tx['confirmations']
        order.confirm_time = current_timestamp() if int(tx['confirmations']) > 0 else 0

        db.session.add(order)
        db.session.commit()

        current_app.logger.debug('new %s deposit, tx: %s, amount: %0.8f' %
                                 (coin, order.tx, order.amount))

    print('process_bch_deposit_task process')

@celery.task
@LockProcessDeco(is_wait=False)
def update_bch_deposit_task():
    records = DiceOrder.query.filter(DiceOrder.coin == coin).\
            filter(DiceOrder.confirmations >= 0).\
            filter(DiceOrder.confirmations < 6).\
            order_by(DiceOrder.id).all()

    for record in records:
        try:
            rpc_client = get_rpc_client(coin)
            r = rpc_client.get_transaction(record.tx)
        except:
            current_app.logger.exception('%s get_transaction fail' % coin)
            continue

        if record.confirmations != r['confirmations']:
            if record.confirmations == 0:
                record.confirm_time = current_timestamp()
            record.confirmations = r['confirmations']
            db.session.commit()

        if record.confirmations <= 0 and current_timestamp() - record.create_time > (7 * 86400):
            record.confirmations = -1
            db.session.commit()
            current_app.logger.error(
                '%s update deposit, tx %s confirming overtime' % (coin, record.tx))

    print('update_bch_deposit_task process')
