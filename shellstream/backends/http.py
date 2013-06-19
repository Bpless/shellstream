#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import logging

from shellstream.utils.requester import RequestHelper
from shellstream.config import HOST

logger = logging.getLogger(__name__)


class TransportError(Exception):
    pass


class HttpTransport(RequestHelper):

    def __init__(self, username=None, password=None, title=None):
        self.host = HOST
        self.username = username
        self.password = password
        self.title = title

        super(HttpTransport, self).__init__()

    def get_endpoint(self, path):
        return "{}{}".format(self.host, path)

    def parse_response(self, response):
        if response.ok:
            res = json.loads(response.content)
            status = res.get("status")
            if status == 200:
                return res.get("content")
            else:
                raise TransportError(res.get("errors"))
        else:
            raise TransportError("Status Code {}:{}".format(response.status_code, response.content))

    def fetch(self, path, data=None, response_callback=None, method="post"):
        endpoint = self.get_endpoint(path)
        response = getattr(self, method)(endpoint, data=data)
        json_response = self.parse_response(response)
        if response_callback:
            response_callback(self, response)
        return json_response

    def create_user(self):
        data = {
                "email": self.username,
                "password": self.password,
                }
        self.fetch("account/api/signup/", data)

    def activate_user(self, url):
        response = self.post(url)
        return self.parse_response(response)

    def authenticate(self):
        def set_session_id(self, response):
            self.session_id = response.cookies.get('session_id')

        data = {
                "email": self.username,
                "password": self.password,
                }


        self.fetch("account/api/login/", data, set_session_id)

    def create_stream(self):
        data = {
                "title": self.title
                }

        content = self.fetch("stream/create/", data)
        self.stream_id = content.get("stream_id")
        self.stream_slug = content.get("stream_slug")
        return self.stream_id, self.stream_slug

    def write_to_stream(self, data):
        data["stream"] = self.stream_id
        self.fetch("stream/write/", data)


transport = HttpTransport
