#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import time
import requests
from werkzeug._compat import to_unicode
from flask import current_app

from .base import Client
from .base import Result

from app.utils import response_code
from app.utils.exceptions import StandardResponseError


class RPCClient(Client):

    @staticmethod
    def get_data(method, params):
        return dict(method=method, params=params, id=int(time.time() * 1000))

    def do_request(self, method, *params, **kwargs):
        url = '{protocol}://{host}:{port}'.format(
                protocol=self.config['protocol'],
                host=self.config['host'],
                port=self.config['port'],
        )
        data = self.get_data(method, params)
        result = requests.request('post', url, timeout=60, data=json.dumps(data), auth=self.config.get('auth'), headers=self.get_headers(), **kwargs)
        if self.logger:
            self.logger.info(self.config.get('auth'))
            msg = 'request {uri} {method}\nheaders: {headers}\nbody: {body}\nstatus_code:{status_code}\nresponse: {resp}'.format(
                    uri=result.request.url,
                    method=result.request.method,
                    headers='; '.join(['{k}: {v}'.format(k=k, v=v) for k, v in self.get_headers().items()]),
                    body=to_unicode(result.request.body, charset='utf-8') if result.request.body is not None else None,
                    status_code=result.status_code,
                    resp=to_unicode(result.content, charset='utf-8')
            )
            self.logger.info(msg)
        rpc_result = RPCResult(result)
        if rpc_result.code != 0:
            raise RuntimeError("rpc: %s error, message: %s url: %s" % (method, rpc_result.message, url))
        return rpc_result


class RPC2Client(RPCClient):
    @staticmethod
    def get_data(method, params):
        return dict(jsonrpc='2.0', method=method, params=params, id=int(time.time() * 1000))


class RPCResult(Result):
    @property
    def result(self):
        if self._result is None:
            self._result = dict(code=response_code.OK, message='OK', data=dict())
            if not self._response.text:
                self._result = None
                return self._result

            data = self._response.json()
            if int(self.status_code) != 200:
                self._result.update(data.get('error'))
                current_app.logger.debug("get rpc result fail, response: " + self._response.text)
            elif data.get('error'):
                self._result.update(data.get('error'))
            else:
                self._result['data'] = data.get('result')

        return self._result

