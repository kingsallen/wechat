from tornado import gen

from handler.base import BaseHandler
from globals import redis
from util.common.decorator import handle_response


class ShortURLRedirector(BaseHandler):
    @handle_response
    @gen.coroutine
    def get(self, uuid):
        url = redis.get('tinyurl_%s' % uuid)
        if url:
            self.redirect(url)
        else:
            self.write_error(http_code=410)
