#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import logging

from shellstream.utils.requester import RequestHelper
from shellstream import HOST

logger = logging.getLogger(__name__)


class TransportError(Exception):
    pass


class HttpTransport(RequestHelper):

    def get_endpoint(self, path):
        return "{0}{1}".format(HOST, path)

    def parse_response(self, response):
        if response.ok:
            try:
                res = json.loads(response.content)
            except TypeError:
                raise TransportError("Bad server response")
            else:
                status = res.get("status")
                if status == 200:
                    return res.get("content")
                else:
                    raise TransportError(res.get("errors"))
        else:
            raise TransportError("Status Code {0}:{1}".format(response.status_code, response.content))

    def fetch(self, path, data=None, response_callback=None, method="post"):
        endpoint = self.get_endpoint(path)
        response = getattr(self, method)(endpoint, data=data)
        json_response = self.parse_response(response)
        if response_callback:
            response_callback(response)
        return json_response

    def set_session_id(self, response):
        self.session_id = response.cookies.get('session_id')
