# coding=utf-8

import uuid
import hmac
import ujson
import hashlib

import redis
from tornado.util import ObjectDict

import conf.common


class SessionData(ObjectDict):
    def __init__(self, session_id, hmac_key):
        super(SessionData, self).__init__(self)
        self.session_id = session_id
        self.hmac_key = hmac_key


class Session(SessionData):
    def __init__(self, session_manager, request_handler, subsession):
        if not isinstance(subsession, int) or subsession <= 0:
            raise Exception(conf.common.SESSION_INDEX_ERROR)

        self.session_manager = session_manager
        self.request_handler = request_handler
        try:
            current_session = self.session_manager.get(subsession,
                                                       request_handler)
        except InvalidSessionException:
            current_session = self.session_manager.get(subsession)

        for k, v in iter(current_session.items()):
            self.update(k=v)

        self.session_id = current_session.session_id
        self.hmac_key = current_session.hmac_key
        self.subsession = subsession

    def save(self):
        self.session_manager.set(self.request_handler, self)


class SessionManager(object):
    def __init__(self, secret, store_options, session_timeout):
        self.secret = secret
        self.session_timeout = session_timeout
        try:
            self.pool = redis.ConnectionPool(host=store_options['redis_host'],
                port=store_options['redis_port'], password=store_options['redis_pass'])
            self.redis = redis.StrictRedis(connection_pool=self.pool)
        except Exception as e:
            print(e)

    def _fetch(self, session_id):
        ret = ObjectDict()
        try:
            raw_data = self.redis.get(session_id)
            if raw_data is not None:
                self.redis.setex(session_id, self.session_timeout, raw_data)
                if isinstance(raw_data, dict):
                    ret = ObjectDict(ujson.loads(raw_data))
        except IOError as e:
            print(e)
        finally:
            return ret

    def get(self, subsession, request_handler=None):
        session_id = None
        hmac_key = None
        if request_handler is not None:
            session_id = request_handler.get_secure_cookie(
                conf.common.COOKIE_SESSION_KEY)
            hmac_key = request_handler.get_secure_cookie(
                conf.common.COOKIE_HMAC_KEY)

        session_exists = True
        if session_id is None:
            session_exists = False
            session_id = self._generate_id()
            hmac_key = self._generate_hmac(session_id)

        check_hmac = self._generate_hmac(session_id)
        if hmac_key != check_hmac:
            raise InvalidSessionException()

        session = SessionData(session_id, hmac_key)

        if session_exists:
            session_data = self._fetch(session_id + "_" + str(subsession))
            for k, v in iter(session_data.items()):
                session.update(k=v)

        return session

    def set(self, request_handler, session):
        request_handler.set_secure_cookie(conf.common.COOKIE_SESSION_KEY,
                                          session.session_id)
        request_handler.set_secure_cookie(conf.common.COOKIE_HMAC_KEY,
                                          session.hmac_key)
        session_data = ujson.dumps(dict(session.items()))
        self.redis.setex(session.session_id + "_" + str(session.subsession),
                         self.session_timeout, session_data)

    def _generate_id(self):
        return hashlib.sha256(self.secret + str(uuid.uuid4())).hexdigest()

    def _generate_hmac(self, session_id):
        return hmac.new(session_id, self.secret, hashlib.sha256).hexdigest()


class InvalidSessionException(Exception):
    pass
