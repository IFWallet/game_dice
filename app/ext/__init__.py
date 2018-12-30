#!/usr/bin/python
# -*- coding: utf-8 -*-

from .log_handler import RedisListHandler

from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from flask_cache import Cache
from flask_babel import Babel
from flask_celery import Celery

db = SQLAlchemy()
redis_store = FlaskRedis(decode_responses=True)
cache = Cache()
babel = Babel()
celery = Celery()
