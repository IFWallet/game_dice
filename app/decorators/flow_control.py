#!/usr/bin/python
# -*- coding: utf-8 -*-

from functools import wraps
from app.utils.utils import request_ip
from app.utils import response_code
from app.utils.exceptions import StandardResponseError
from app.ext import redis_store
from app.utils.utils import get_func_fullname



class RequestFlowControl(object):
    def __init__(self, seconds, count, func_name=None):
        self.seconds = seconds
        self.count = count
        self.func_name = func_name

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.func_name:
                self.func_name = get_func_fullname(func)

            ey = 'flow_control:{func_name}:{request_ip}:{seconds}'.format(
                func_name=self.func_name,
                request_ip=request_ip(),
                seconds=self.seconds)

            if not redis_store.exists(key):
                redis_store.setex(key, self.seconds, 0)
            flow_count = redis_store.incr(key)
            if flow_count > self.count:
                raise StandardResponseError(response_code.TOO_FREQUENTLY)
            return func(*args, **kwargs)

        return wrapper
