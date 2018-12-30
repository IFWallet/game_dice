#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask_babel import gettext as _

OK = 0
ERROR = 1
INVALID_ARGUMENT = 2
INTERNAL_ERROR = 3
TOO_FREQUENTLY = 4
FAIL_TOO_FREQUENTLY = 5

UN_AUTHORIZATION = 401
FORBIDDEN = 403
PAGE_NOT_FOUND = 404
INVALID_TOKEN = 405

MESSAGES = {
    0: _('OK'),
    1: _('Error'),
    2: _('Invalid argument'),
    3: _('Internal error'),
    4: _('Too frequently'),
    5: _("Failed too frequently"),

    401: _('Please login'),
    403: _("Operation Forbidden"),
    404: _('Page not found'),
    405: _('Invalid visit token'),
}


def get_message_by_code(code):
    return MESSAGES.get(code, '')
