#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
from functools import wraps
from flask import request
from flask import current_app
from flask_babel import gettext as _

from app.utils.exceptions import StandardResponseError
from app.utils.utils import get_func_fullname
from app.utils.caches import LockProcessCache


class LockProcessDeco(object):
    def __init__(self, is_wait=True, func_name=''):
        self.is_wait = is_wait
        self.func_name = func_name

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.func_name:
                self.func_name = get_func_fullname(func)
            lock_process_cache = LockProcessCache(self.func_name)
            if not self.is_wait and lock_process_cache.is_lock():
                message = '{func_name} is lock, abort execute'.format(
                    func_name=self.func_name)
                current_app.logger.info(message)
                raise StandardResponseError(message)
            try:
                lock_process_cache.lock()
                return func(*args, **kwargs)
            finally:
                lock_process_cache.unlock()
        return wrapper

