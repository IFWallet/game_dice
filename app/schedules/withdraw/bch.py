import decimal

from flask import g
from flask import current_app

from app.ext import db
from app.ext import celery

from app.models import Block
from app.models import DiceOrder
from app.models import RewardHistory

from app.utils.utils import quantize
from app.utils.utils import strfdecimal
from app.utils.utils import strftime
from app.utils.utils import current_timestamp

from app.utils.enums.coin_type import CoinType
from app.utils.rpc import get_rpc_client
from app.utils.wallet import get_tx_outputs

from app.decorators.process import LockProcessDeco

coin = CoinType.BCH
require_confirmations = 6

@celery.task
@LockProcessDeco(is_wait=False)
def sync_bch_block_task():
    rpc_client = get_rpc_client(coin)
    curr_height = rpc_client.get_block_count()
    latest_block = Block.query.order_by(Block.height.desc()).first()
    if not latest_block:
        local_height = curr_height - 3
    else:
        local_height = latest_block.height

    while local_height < curr_height:
        block_hash = rpc_client.get_block_hash(local_height + 1)
        if not block_hash:
            return

        res = rpc_client.get_block(block_hash)
        if not res:
            return

        block = Block()
        block.coin = coin
        block.height = res['height']
        block.tx_count = len(res['tx'])
        block.confirmations = res['confirmations']
        block.confirm_time = current_timestamp() if block.confirmations > 0 else 0

        db.session.add(block)
        db.session.commit()

        local_height += 1


@celery.task
@LockProcessDeco(is_wait=False)
def update_bch_block_task():
    rpc_client = get_rpc_client(coin)
    curr_height = rpc_client.get_block_count()
    print(curr_height)
    blocks = Block.query.filter(Block.height <= curr_height).\
            filter(Block.confirmations < require_confirmations).\
            order_by(Block.id).all()

    for block in blocks:
        block_hash = rpc_client.get_block_hash(block.height)
        if not block_hash:
            return
        res = rpc_client.get_block(block_hash)
        if not res:
            return

        block.confirmations = res['confirmations']

        db.session.commit()

    alloc_bch_reward_task()


@celery.task
@LockProcessDeco(is_wait=False)
def alloc_bch_reward_task():
    blocks = Block.query.filter(Block.coin == coin).\
            filter(Block.confirmations > 1).\
            filter(Block.is_reward == False).all()

    for block in blocks:
        print(block.height)
        even_orders = DiceOrder.query.filter(DiceOrder.coin == coin).\
                filter(DiceOrder.game_round == block.height).\
                filter(DiceOrder.choice == 0).\
                filter(DiceOrder.confirmations > 0).all()
        even_total = sum([order.amount for order in even_orders])

        odd_orders = DiceOrder.query.filter(DiceOrder.coin == coin).\
                filter(DiceOrder.game_round == block.height).\
                filter(DiceOrder.choice == 1).\
                filter(DiceOrder.confirmations > 0).all()
        odd_total = sum([order.amount for order in odd_orders])

        reward_total = min(odd_total, even_total)
        tx_fee = decimal.Decimal('0.00002')

        if block.tx_count % 2 == 1: # odd win
            for order in odd_orders:
                reward_amount = (reward_total * order.amount / odd_total) + order.amount
                if reward_amount < tx_fee:
                    continue

                reward = RewardHistory()
                reward.coin = coin
                reward.address = order.from_address
                reward.amount = max(reward_amount - tx_fee, 0)
                reward.tx_fee = tx_fee
                reward.business = 'reward'
                reward.game_round = block.height

                db.session.add(reward)

            if even_total > odd_total:
                for order in even_orders:
                    return_amount = (even_total - reward_total) * (order.amount / even_total)

                    if reward_amount < tx_fee:
                        continue

                    reward = RewardHistory()
                    reward.coin = coin
                    reward.address = order.from_address
                    reward.amount = max(return_amount - tx_fee, 0)
                    reward.tx_fee = tx_fee
                    reward.business = 'return'
                    reward.game_round = block.height

                    db.session.add(reward)

        else: # even win
            for order in even_orders:
                reward_amount = (reward_total * order.amount / even_total) + order.amount

                if reward_amount < tx_fee:
                    continue

                reward = RewardHistory()
                reward.coin = coin
                reward.address = order.from_address
                reward.amount = max(reward_amount - tx_fee, 0)
                reward.tx_fee = tx_fee
                reward.business = 'reward'
                reward.game_round = block.height

                db.session.add(reward)

            if odd_total > even_total:
                for order in odd_orders:
                    return_amount = (odd_total - reward_total) * (order.amount / odd_total)
                    if return_amount < tx_fee:
                        continue

                    reward = RewardHistory()
                    reward.coin = coin
                    reward.address = order.from_address
                    reward.amount = max(return_amount - tx_fee, 0)
                    reward.tx_fee = tx_fee
                    reward.business = 'return'
                    reward.game_round = block.height

                    db.session.add(reward)

        block.is_reward = True
        db.session.commit()
        print("alloc_bch_reward_task process")


@celery.task
@LockProcessDeco(is_wait=False)
def send_bch_reward_task():
    blocks = Block.query.filter(Block.coin == coin).\
            filter(Block.is_reward == True).\
            filter(Block.reward_tx == None).all()

    for block in blocks:
        records = RewardHistory.query.\
            filter(RewardHistory.coin == coin).\
            filter(RewardHistory.tx == None).\
            filter(RewardHistory.game_round == block.height).\
            order_by(RewardHistory.amount).all()
        if not records:
            return

        rpc_client = get_rpc_client(coin)
        available_balance, available_txs = rpc_client.get_unspent_txs(['game_dice'], 1)
        if not available_balance:
            current_app.logger.error("%s no available balance for withdraw" % coin)
            return

        process_records = []
        process_amount = decimal.Decimal('0')
        for record in records:
            if process_amount + record.amount + record.tx_fee <= available_balance:
                process_records.append(record)
                process_amount += decimal.Decimal(record.amount)
            else:
                current_app.logger.error('%s hot wallet balance not enough' % coin)
                break

        if process_amount == 0:
            current_app.logger.debug('%s nothing to withdraw' % coin)
            return

        total_output_amount = decimal.Decimal('0')
        total_fee = decimal.Decimal('0.00005')
        real_process_records = []
        tx_outputs = {}

        for record in process_records:
            tx_outputs.setdefault(record.address, 0)
            tx_outputs[record.address] += record.amount
            total_output_amount += record.amount
            real_process_records.append(record)

        if len(real_process_records) == 0:
            return

        for address in tx_outputs:
            tx_outputs[address] = float(tx_outputs[address])

        tx_inputs = []
        total_input_amount = decimal.Decimal('0')

        for tx in available_txs:
            tx_inputs.append({'txid': tx['txid'], 'vout': tx['vout']})
            total_input_amount += decimal.Decimal(str(tx['amount']))
            if total_input_amount >= total_output_amount + total_fee:
                break

        tx_fee_kb = decimal.Decimal('0.00001')
        real_fee = rpc_client.get_fee(tx_inputs, tx_outputs, tx_fee_kb, total_fee)

        if total_input_amount > total_output_amount + real_fee:
            tx_outputs, rest_amount = get_tx_outputs(
                coin, tx_outputs, (total_input_amount - total_output_amount - real_fee))

        real_fee += rest_amount

        current_app.logger.debug(
            "%s tx_inputs: %s\ntx_outputs: %s", coin, str(tx_inputs), str(tx_outputs))
        current_app.logger.debug("%s input amount: %s, output amount: %s", coin, str(
            total_input_amount), str(total_output_amount))

        tx_outputs['data'] = 'reward of game.cash in round #' + str(block.height)
        txid = rpc_client.send_transaction(tx_inputs, tx_outputs)
        for record in real_process_records:
            record.confirmations = 0
            record.tx = txid

        db.session.flush()
        db.session.commit()

    print('send_bch_reward_task process')

