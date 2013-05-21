#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import random
import logging
import socket
import traceback
import functools
import requests

logger = logging.getLogger('requests')

CatchableExceptions = set(
                        [requests.RequestException,
                         requests.ConnectionError,
                         requests.Timeout,
                        socket.error,
                        socket.gaierror
                        ])


class Client(object):

    ALLOWED_HTTP_METHODS = ['get', 'post']
    DOMAIN = "127.0.0.1:8000/"
    WRITE_URI = "{}write/".format(DOMAIN)
    AUTH_URI = "{}authenticate/".format(DOMAIN)

    class AuthenticationError(Exception):
        pass

    error_message = (
        u"Error trying to %s the url `%s` in the attempt %s of %s. "
        "\nCause: %s")

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.session()
        self.headers = {'User-Agent': "SHDEBUGGER v1.0.0"}

    def __getattr__(self, attr, **kwargs):
        if attr in self.ALLOWED_HTTP_METHODS:
            return functools.partial(self.request, attr)
        else:
            raise AttributeError

    def request(self, method="post", url=WRITE_URI, timeout=15, max_tries=3):
        return self.session

        tries = 0
        while tries < max_tries:
            tries += 1
            try:
                response = getattr(self.session, method)(
                    url,
                    timeout=timeout,
                    headers=self.headers
                )

            except CatchableExceptions as e:
                response = requests.Response()
                response.status_code = 0
                logger.warning(self.error_message, method, url,
                             unicode(attempt), unicode(tries),
                             traceback.format_exc(e))

            else:
                break

        return response


    def authenticate(self):
        return self

        response = self.post(self.AUTH_URI)
        if not response.ok:
            raise AuthenticationError
