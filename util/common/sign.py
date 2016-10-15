# -*- coding: utf-8 -*-

import time
import random
import string
import hashlib


class Sign(object):
    def __init__(self, jsapi_ticket="", url="", ret=None):
        if not ret:
            self.ret = {
                'nonceStr': self._create_nonce_str(),
                'jsapi_ticket': jsapi_ticket,
                'timestamp': self._create_timestamp(),
                'url': url
            }
        else:
            self.ret = ret

    def sign(self, url=None, keyname="signature"):
        if url:
            self.ret["url"] = url
        temp_str = '&'.join(
            ['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)
             if key != "_default" and key != 'key' and self.ret[key]])
        if "key" in self.ret:
            temp_str = temp_str + "&key=" + self.ret["key"]
        temp_str = temp_str.encode("utf-8")
        self.ret[keyname] = hashlib.sha1(temp_str).hexdigest()
        return self.ret

    @staticmethod
    def _create_nonce_str():
        return ''.join(random.choice(string.ascii_letters + string.digits)
                       for _ in range(15))

    @staticmethod
    def _create_timestamp():
        return int(time.time())
