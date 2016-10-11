# coding=utf-8

import ujson
from service.data.base import cache
import tornado.gen as gen
from tornado.util import ObjectDict
from abc import ABCMeta, abstractmethod
from utils.common.sign import Sign
from utils.tool.http_tool import http_get
from app import logger


class SessionDataService(object):
    pass


class IDBFetchable(object):

    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        self.exist = False
        self.logger = logger

    @abstractmethod
    def fetch_from_db(self, **kwargs):
        pass

    def set_from_dict(self, d):
        if not d:
            return self
        for k, v in d.iteritems():
            setattr(self, k, v)
        self.exist = True
        return self

    def to_dict(self, *args):
        return {k: v for k, v in self.__dict__.iteritems()
                if k not in ["LOG", "_db", "kwargs"] + list(args)}

    def get(self, item, default=None):
        res = getattr(self, item)
        return res if res else default

    def __repr__(self, *args):
        d = self.to_dict(*args)
        return ujson.dumps(d, encoding='utf-8', ensure_ascii=False)

    @staticmethod
    def valid_conds(conds):
        return not conds or not (isinstance(conds, dict) or isinstance(conds, str))

    def __nonzero__(self):
        return self.exist


class JsApi(object):
    def __init__(self, jsapi_ticket, url):
        self.sign = Sign(jsapi_ticket=jsapi_ticket)
        self.__dict__.update(self.sign.sign(url=url))


class Wechat(IDBFetchable):
    """current_user.wechat"""
    def __init__(self, **kwargs):
        super(Wechat, self).__init__(**kwargs)
        self.signature = kwargs.get("signature", "")

    @gen.coroutine
    def fetch_from_db(self):
        if not self.signature:
            gen.Return(None)
        res = yield self.get_wechat_by_signature(self.signature)

        self.exist = True
        raise gen.Return(res)

    @gen.coroutine
    def get_wechat_by_signature(self):
        ret = yield self.get_wechat(conds={"signature", [self.signature, "="]})
        raise gen.Return(ret)

    @cache(ttl=60)
    @gen.coroutine
    def get_wechat(self, conds, fields=None):
        if not self.valid_conds(conds):
            self.logger.warn(u"Warning:[get_wechat][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(None)

        if not fields:
            fields = self.hr_wx_wechat_dao.fields_map.keys()

        res = yield self.hr_wx_wechat_dao.get_record_by_conds(conds, fields)
        raise gen.Return(res)


class WxUser(IDBFetchable):
    """Work for both current_user.wxuser and current_user.qxuser
    """
    def __init__(self, **kwargs):
        super(WxUser, self).__init__(**kwargs)
        self.unionid = kwargs.get("unionid", "")
        self.wechat_id = kwargs.get("wechat_id", "")
        self.exist = False

    @gen.coroutine
    def fetch_from_db(self):
        res = {}
        if not self.unionid or not self.wechat_id:
            gen.Return(None)
        res = yield self.get_wxuser(conds={
            "wechat_id", [self.wechat_id, "="],
            "unionid", [self.unionid, "="]})
        self.exist = True
        raise gen.Return(res)

    @cache(ttl=60)
    @gen.coroutine
    def get_wxuser(self, conds, fields=None):
        if not self.valid_conds(conds):
            self.logger.warn(u"Warning:[get_wxuser][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(None)

        if not fields:
            fields = self.user_wx_user_dao.fields_map.keys()

        res = yield self.user_wx_user_dao.get_record_by_conds(conds, fields)
        raise gen.Return(res)


class Employee(IDBFetchable):
    def __init__(self, **kwargs):
        self.wxuser_id = kwargs.get("wxuser_id", "")
        self.company_id = kwargs.get("company_id", "")

    @gen.coroutine
    def fetch_from_db(self):
        if not self.wxuser_id or not self.company_id:
            gen.Return(None)
        res = yield self.get_employee(conds={
            "wxuser_id", [self.wxuser_id, "="],
            "company_id", [self.company_id, "="],
            "disable", ["0", "="],
            "activation", ["0", "="],
            "status", ["0", "="]
        })
        self.exist = True
        raise gen.Return(res)

    @cache(ttl=60)
    @gen.coroutine
    def get_employee(self, conds, fields=None, ):
        if not self.valid_conds(conds):
            self.logger.warn(u"Warning:[get_employee][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(None)

        if not fields:
            fields = self.user_employee_dao.fields_map.keys()

        res = yield self.user_employee_dao.get_record_by_conds(conds, fields)
        raise gen.Return(res)


class Recom(IDBFetchable):
    def __init__(self, **kwargs):
        self.openid = kwargs.get("recom_id", None)

    @gen.coroutine
    def fetch_from_db(self):
        if not self.openid:
            gen.Return(None)

        res = yield self.get_recom(conds={
            "openid", [self.openid, "="],
        })
        self.exist = True
        raise gen.Return(res)

    @cache(ttl=60)
    @gen.coroutine
    def get_recom(self, conds, fields=None, ):
        if not self.valid_conds(conds):
            self.logger.warn(u"Warning:[get_recom][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(None)

        if not fields:
            fields = self.user_wx_user_dao.fields_map.keys()

        res = yield self.user_wx_user_dao.get_record_by_conds(conds, fields)
        raise gen.Return(res)


class SysUser(IDBFetchable):
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)

    @gen.coroutine
    def fetch_from_db(self):
        if not self.id:
            gen.Return(None)
        res = yield self.get_user(params={"user_id": self.id})
        self.exist = True
        raise gen.Return(res)

    @cache(ttl=60)
    @gen.coroutine
    def get_user(self, params):
        user = yield http_get(
            "user", jdata=params, timeout=5, infra=True)
        user_setting = yield http_get(
            "user/settings", jdata=params, timeout=5, infra=True)
        user = ObjectDict(user)
        user_setting = ObjectDict(user_setting)
        user.user_setting = user_setting
        raise gen.Return(user)


class SessionBundle(ObjectDict):
    def __init__(self, session_id):
        self._session_id = session_id
        self.wxuser = None
        self.qxuser = None
        self.employee = None
        self.sysuser = None
        self.recom = None
        self.company = None
        self.wechat = None
        self.loaded = False

    def load_data(self, wxuser, qxuser, employee, sysuser, recom, company, wechat):
        self.wxuser = wxuser
        self.qxuser = qxuser
        self.employee = employee
        self.sysuser = sysuser
        self.recom = recom
        self.company = company
        self.wechat = wechat
        self.loaded = True

    def __nonzero__(self):
        return self.loaded
