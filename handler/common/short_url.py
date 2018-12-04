import datetime

from tornado import gen
import shortuuid

from handler.base import BaseHandler
from globals import redis
from util.common.decorator import handle_response


class ShortURLGenerator(BaseHandler):
    @handle_response
    @gen.coroutine
    def post(self):
        url = self.json_args['url']
        uuid = self._generate_short_url(url)
        short_url = self.make_url('/s/{}'.format(uuid))
        self.send_json_success({'url': short_url})

    def _generate_uuid_and_redis_key(self):
        uuid = shortuuid.ShortUUID().random(length=8)
        key = 'tinyurl_%s' % uuid
        return uuid, key

    def _generate_uuid(self, url):
        uuid, key = self._generate_uuid_and_redis_key()
        while redis.exists(key):
            uuid, key = self._generate_uuid_and_redis_key()
        redis.setex(key, datetime.timedelta(days=4), url)
        return uuid


class ShortURLRedirector(BaseHandler):
    @handle_response
    @gen.coroutine
    def get(self, uuid):
        url = redis.get('tinyurl_%s' % uuid)
        if url:
            self.redirect(url)
        else:
            self.write_error(http_code=410)
