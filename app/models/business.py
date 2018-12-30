from app.ext import db
from app.utils.utils import current_timestamp


class DiceOrder(db.Model):
    __tablename__ = 'dice_order'
    __table_args__ = (
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'})

    id          = db.Column(db.Integer, db.Sequence('dice_order_id_seq'), primary_key=True)
    create_time = db.Column(db.Integer, default=current_timestamp)

    coin        = db.Column(db.String(10))
    game_round 	= db.Column(db.Integer, default=0) # round

    from_address = db.Column(db.String(64))
    address     = db.Column(db.String(64))
    tx          = db.Column(db.String(100))
    vout        = db.Column(db.Integer, default=0)
    amount      = db.Column(db.Numeric(precision='20,8'), nullable=False)
    choice      = db.Column(db.Integer, default=0) # 0 for even, 1 for odd

    confirmations = db.Column(db.Integer, default=0)
    confirm_time = db.Column(db.Integer, nullable=True)
    is_reward   = db.Column(db.Boolean, default=False)


class RewardHistory(db.Model):
    __tablename__ = 'reward_history'
    __table_args__ = (
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'})

    id          = db.Column(db.Integer, db.Sequence('reward_history_id_seq'), primary_key=True)
    create_time = db.Column(db.Integer, default=current_timestamp)
    update_time = db.Column(db.Integer, onupdate=current_timestamp)

    game_round  = db.Column(db.Integer)

    coin        = db.Column(db.String(10))
    address     = db.Column(db.String(64))
    tx          = db.Column(db.String(100))
    vout        = db.Column(db.Integer, default=0)
    amount      = db.Column(db.Numeric(precision='20,8'), nullable=False)
    tx_fee      = db.Column(db.Numeric(precision='20,8'), nullable=True)
    business    = db.Column(db.String(10))

    confirmations = db.Column(db.Integer, default=0)
    confirm_time = db.Column(db.Integer, nullable=True)


class Block(db.Model):
    __tablename__ = 'block'
    __table_args__ = (
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'})

    id          = db.Column(db.Integer, db.Sequence('block_id_seq'), primary_key=True)
    create_time = db.Column(db.Integer, default=current_timestamp)

    coin        = db.Column(db.String(10))
    height      = db.Column(db.Integer, default=0)
    tx_count    = db.Column(db.Integer, default=0)
    confirmations   = db.Column(db.Integer, default=0)
    confirm_time    = db.Column(db.Integer, nullable=True)

    is_reward       = db.Column(db.Boolean, default=False)
    reward_tx       = db.Column(db.String(100))


