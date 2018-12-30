#!/usr/bin/python
# -*- coding: utf-8 -*-


class Client(object):
    default_headers = (
        ('Content-Type', 'application/json;charset=utf-8'),
    )

    def __init__(self, config, logger=None, headers=None) :
        self.config = config
        self.logger = logger
        headers = headers if headers else ()
        self.__headers = headers + self.default_headers

    def get_headers(self):
        d = {}
        for k, v in self.__headers:
            d[k] = v
        return d


class Result(object):
    def __init__(self, response):
        self._data = None
        self._result = None
        self._response = response

    @property
    def result(self):
        raise NotImplemented

    @property
    def data(self):
        if not self.result:
            return None
        return self.result['data']

    @property
    def message(self):
        if not self.result:
            return None
        return self.result['message']

    @property
    def code(self):
        if not self.result:
            return 0
        return int(self.result['code'])

    @property
    def status_code(self):
        return self._response.status_code

    def __getattr__(self, item):
        if not self.result:
            return None
        return self.result[item]
