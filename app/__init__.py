import os
import logging
import datetime
import json
import pytz
from logging.handlers import RotatingFileHandler

from flask import g
from flask import Flask
from flask import current_app
from flask import request
from flask import session
from flask import make_response
from flask import jsonify
from flask import render_template

from flask.ext.babel import gettext

from app.views import view_configure_blueprint
from app.ext.log_handler import RedisListHandler
from app.ext import db
from app.ext import babel
from app.ext import cache
from app.ext import celery
from app.ext import redis_store
from app.ext.log_handler import RedisListHandler
from app.utils.xhr import *
from app.utils.utils import static_url
from app.utils.utils import strftime
from app.utils.utils import strfdecimal
from app.utils.utils import coin_txid_url
from app.utils.utils import coin_address_url
from app.utils.utils import coin_block_hash_url


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('setting.py')
    if os.path.exists(os.path.join(app.root_path, 'testing.py')):
        print('load test config')
        app.debug = True
        app.config.from_pyfile('testing.py')

    configure_jinja(app)
    configure_extensions(app)
    configure_logging(app)
    configure_befor_handlers(app)
    configure_blueprint(app)

    return app


def configure_blueprint(app):
    view_configure_blueprint(app)


def configure_extensions(app):
    db.init_app(app)
    babel.init_app(app)
    cache.init_app(app)
    redis_store.init_app(app)
    celery.init_app(app)
    celery.config_from_object('app.celeryconfig')

    # @babel.localeselector
    # def get_locale():
    #     return g.lang


def configure_logging(app):
    app.logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(asctime)s] (%(levelname)s):%(filename)s:%(funcName)s:%(lineno)d: %(message)s')

    redis_log_handler = RedisListHandler(
        app.config['ALERT_REDIS_URL'], 'alert:message')
    redis_log_handler.setLevel(logging.ERROR)
    redis_log_handler.setFormatter(formatter)
    app.logger.addHandler(redis_log_handler)

    local_log_handler = RotatingFileHandler(
        '/var/log/game_dice/game_dice.log', maxBytes=20*1024*1024, backupCount=20)
    local_log_handler.setFormatter(formatter)
    local_log_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(local_log_handler)


def configure_befor_handlers(app):
    @app.before_request
    def setup_timezone():
        g.tz = pytz.timezone(current_app.config.get('TIMEZONE'))

    @app.before_request
    def setup_env():
        g.testing = app.config.get('TESTING', False)
        g.page_cap = int(current_app.config.get('PAGE_CAPACITY', '20'))

def configure_jinja(app):
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    app.jinja_env.globals['static_url'] = static_url
    app.jinja_env.globals['strftime'] = strftime
    app.jinja_env.globals['strfdecimal'] = strfdecimal
    app.jinja_env.globals['coin_txid_url'] = coin_txid_url
    app.jinja_env.globals['coin_address_url'] = coin_address_url
    app.jinja_env.globals['coin_block_hash_url'] = coin_block_hash_url


