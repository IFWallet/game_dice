#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from flask_babel import gettext as _

from app.utils import response_code


class StandardResponseError(Exception):
    def __init__(self, code=response_code.ERROR, message='', data=dict()):
        self.code = code
        self.data = data
        if not message:
            self.message = response_code.MESSAGES.get(code, 'error')
        else:
            self.message = message

class UnAuthorizationError(Exception):
    def __init__(self):
        self.code = response_code.UN_AUTHORIZATION
        self.data = dict()
        self.message = _('Please login')

