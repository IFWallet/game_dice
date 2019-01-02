import time
import json
import decimal

from flask import g
from flask import Blueprint
from flask import abort
from flask import redirect
from flask import url_for
from flask import current_app
from flask import make_response
from flask import render_template
from flask import request
from flask import flash

from app.utils.xhr import request_ok
from app.utils.xhr import request_error

from app.ext import redis_store
from app.models import Block
from app.models import DiceOrder
from app.models import RewardHistory

from app.utils.rpc import get_rpc_client
from app.utils.utils import current_timestamp
from app.utils.enums.coin_type import CoinType


mod = Blueprint('game', __name__)

coin = CoinType.BCH

@mod.route('/', methods=['GET'])
def index():
    try:
        page = int(request.args.get('page', '1'))
        page = page if page > 0 else 1
        page_cap = 20
        open_in_wallet = int(request.args.get('in_wallet', '0'))
    except:
        return redirect(url_for('game.index'))

    even_address = current_app.config['CHOICE_ADDRESSES'][coin][0]
    odd_address = current_app.config['CHOICE_ADDRESSES'][coin][1]

    rpc_client = get_rpc_client(coin)
    curr_height = rpc_client.get_block_count()
    curr_round = curr_height + 1

    odd_orders = DiceOrder.query.filter(DiceOrder.game_round == curr_round).\
            filter(DiceOrder.choice == 1).\
            order_by(DiceOrder.id.desc()).all()
    total_odd_amount = sum([order.amount for order in odd_orders])

    even_orders = DiceOrder.query.filter(DiceOrder.game_round == curr_round).\
            filter(DiceOrder.choice == 0).\
            order_by(DiceOrder.id.desc()).all()
    total_even_amount = sum([order.amount for order in even_orders])

    max_amount = max(total_odd_amount, total_even_amount)
    max_amount = max(max_amount, 0.00000001) # not divide by 0

    blocks = Block.query.order_by(Block.height.desc()).\
            slice((page - 1) * page_cap, page * page_cap).all()

    return render_template('index.html', coin=coin, curr_round=curr_round, blocks=blocks,
            page=page, page_cap=page_cap, prev_page=(page > 1), next_page=(len(blocks) == page_cap),
            even_address=even_address, odd_address=odd_address,
            total_odd_amount=total_odd_amount, total_even_amount=total_even_amount, max_amount=max_amount,
            odd_orders=odd_address, even_orders=even_orders, open_in_wallet=open_in_wallet)

@mod.route('/orders/odd/')
def odd_orders():
    try:
        page = int(request.args.get('page', '1'))
        page = 1 if page <= 0 else page
        height = int(request.args.get('round', '0'))
    except:
        return request_error(10, "invalid arguments")

    if not height:
        return request_error(10, "invalid arguments")

    query = DiceOrder.query.filter(DiceOrder.coin == coin).\
            filter(DiceOrder.game_round == height).\
            filter(DiceOrder.choice == 1)
    pagination = query.order_by(DiceOrder.id.desc()).paginate(page, 10, error_out=False)
    html = render_template('order_list.html', records=pagination.items,
            pagination=pagination, coin=coin)
    return request_ok({'html': html})

@mod.route('/orders/even/')
def even_orders():
    try:
        page = int(request.args.get('page', '1'))
        page = 1 if page <= 0 else page
        height = int(request.args.get('round', '0'))
    except:
        return request_error(10, "invalid arguments")

    if not height:
        return request_error(10, "invalid arguments")

    query = DiceOrder.query.filter(DiceOrder.coin == coin).\
            filter(DiceOrder.game_round == height).\
            filter(DiceOrder.choice == 0)
    pagination = query.order_by(DiceOrder.id.desc()).paginate(page, 10, error_out=False)
    html = render_template('order_list.html', records=pagination.items,
            pagination=pagination, coin=coin)
    return request_ok({'html': html})

@mod.route('/reward/history/')
def reward_history():
    try:
        page = int(request.args.get('page', '1'))
        page = 1 if page <= 0 else page
        game_round = int(request.args.get('round', '0'))
    except:
        return request_error(10, "invalid arguments")

    if not game_round:
        return request_error(10, "invalid arguments")

    query = RewardHistory.query.filter(RewardHistory.coin == coin).\
            filter(RewardHistory.game_round == game_round)

    pagination = query.order_by(RewardHistory.id.desc()).paginate(page, 10, error_out=False)
    html = render_template('reward_list.html', records=pagination.items,
            pagination=pagination, coin=coin)
    return request_ok({'html': html})

