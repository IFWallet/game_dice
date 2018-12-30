#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from decimal import Decimal


def email(str_email):
    if len(str_email) > 64:
        raise ValueError('Invalid email')

    if re.match('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', str_email):
        return str_email.lower()

    raise ValueError('Invalid email')

def str_upper(str_argument):
    return str_argument.upper()

def str_lower(str_argument):
    return str_argument.lower()

def str_strip(str_argument):
    return str_argument.strip()

def abs_decimal(value):
    if not value:
        return Decimal(0)

    value = Decimal(value)
    return abs(value)


def positive_decimal(value):
    if not value:
        raise ValueError('{value} less than zero'.format(value=value))
    value = Decimal(value)
    if value <= Decimal(0):
        raise ValueError('{value} less than zero'.format(value=value))

    return value


def str_not_null(value):
    if not value:
        raise ValueError('Can not be null')
    return value

