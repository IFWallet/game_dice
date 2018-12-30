#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
import socket
import logging

class RedisListHandler(logging.Handler):
    def __init__(self, url, key):
        logging.Handler.__init__(self)
        self.key = key
        self.redis_client = redis.StrictRedis.from_url(url)

    def emit(self, record):
        self.redis_client.rpush(self.key, self.format(record))

