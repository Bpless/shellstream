#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import socket
import traceback
import functools
import requests

logger = logging.getLogger('requests')

ConnectionErrors = [requests.RequestException,
                         requests.ConnectionError,
                         requests.exceptions.ConnectionError,
                         requests.Timeout,
                        socket.error,
                        socket.gaierror
                        ]


class RequestHelper(object):

    error_message = (
        u"Error trying to %s the url `%s` in the attempt %s of %s. "
        "\nCause: %s")

    def __init__(self, **kwargs):
        self.allowed_http_methods = kwargs.get("allowed_http_methods", ["get", "post"])
        self.session = requests.session()
        self.headers = {'User-Agent': "SHELL_STREAMER v1.0.0"}

    def __getattr__(self, attr, **kwargs):
        if attr in self.allowed_http_methods:
            return functools.partial(self.request, attr)
        else:
            raise AttributeError

    def request(self, method, url, data=None, timeout=15, max_tries=3):

        tries = 0
        while tries < max_tries:
            tries += 1
            try:
                response = getattr(self.session, method)(
                    url,
                    data=data,
                    timeout=timeout,
                    headers=self.headers
                )

            except tuple(ConnectionErrors), e:
                response = type("ResponseMock", (object,), {"ok": False, "status_code": 503})
                response.content = "ShellStreamer seems to be having some connection issues"
                logger.warning(self.error_message, method, url,
                             unicode(tries),
                             traceback.format_exc(e))
            else:
                break

        return response
