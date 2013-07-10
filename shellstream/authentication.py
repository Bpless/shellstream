###### MUCH OF THIS CODE TAKEN FROM python-firebase ######
######  firebase_token_generator.py ##########
import base64
import hashlib
import hmac

__all__ = ['TokenGenerator']


class TokenGenerator(object):

    def __init__(self, token):
        assert token, 'Your ShellStream TOKEN is not valid (cause you do not list one)'
        self.token = token

    def _encode(self, bytes):
        encoded = base64.urlsafe_b64encode(bytes)
        return encoded.decode('utf-8').replace('=', '')

    def encode_token(self):
        def portable_bytes(s):
            try:
                return bytes(s, 'utf-8')
            except TypeError:
                return bytes(s)

        TOKEN_SECRET = portable_bytes(self.token)
        BASE_STRING = "SHELLSTREAM"
        return self._encode(hmac.new(TOKEN_SECRET, BASE_STRING,
                                     hashlib.sha256).digest())
