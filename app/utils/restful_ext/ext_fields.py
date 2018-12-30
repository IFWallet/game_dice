#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from flask_restful.fields import Raw
from app.utils.utils import strfdecimal

class ConvertToJson(Raw):
    """
    A decimal number with a fixed precision.
    """
    def format(self, value):
        if not value:
            return dict()

        return json.loads(value)


class StrDecimal(Raw):
    def __init__(self, places=2, **kwargs):
        super(StrDecimal, self).__init__(**kwargs)
        self.places = places

    def format(self, value):
        return strfdecimal(value, self.places)


