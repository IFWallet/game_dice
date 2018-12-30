#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import jsonify
from flask.ext.babel import gettext as _
from app.utils import response_code


def request_ok(result):
    return jsonify(error={'code': 0, 'message': 'ok'}, result=result)

def request_error(code, message=None):
    if message == None:
        message = _(response_code.MESSAGES[code])
    return jsonify(error={'code': code, 'message': message}, result=None)

def response_ok(data=dict(), message=''):
    if not message:
        message = _('OK')
    return jsonify(dict(code=response_code.OK, message=message, data=data))


def response_error(code=response_code.ERROR, message='', data=dict()):
    if not message:
        message = response_code.MESSAGES.get(code, response_code.ERROR)
    return jsonify(dict(code=code, message=_(message), data=data))
