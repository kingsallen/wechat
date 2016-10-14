# coding=utf-8

import time

from tornado import gen

from service.data.base import DataService, cache


class UserWxUserDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_wxuser(self, openid=None, wechat_id=None):
        if not openid or not wechat_id:
            self.logger.warn(u"Warning:[get_wxuser][invalid parameters], Detail:[openid: {0}, wechat_id: {1}]".format(openid, wechat_id))
            raise gen.Return(None)

        conds = {
            "openid": [str(openid), "="],
            "wechat_id": [str(wechat_id), "="]
        }
        fields = self.user_wx_user_dao.fields_map.keys()

        response = yield self.user_wx_user_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @cache(ttl=60)
    @gen.coroutine
    def get_wxuser(self, id=None):
        if not id:
            self.logger.warn(u"Warning:[get_wxuser][invalid parameters], Detail:[id: {0}]".format(id))
            raise gen.Return(None)

        conds = {"id": [str(id), "="]}
        fields = self.user_wx_user_dao.fields_map.keys()

        response = yield self.user_wx_user_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @cache(ttl=60)
    @gen.coroutine
    def get_wxuser(self, conds=None, fields=None):
        if not conds or not fields:
            self.logger.warn(u"Warning:[get_wxuser][invalid parameters], Detail:[conds: {0}, fields: {1}]".format(conds, fields))
            raise gen.Return(None)

        fields = fields or self.user_wx_user_dao.fields_map.keys()

        response = yield self.user_wx_user_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @gen.coroutine
    def create_wxuser(self, userinfo=None, wechat_id=None):
        if not userinfo or not wechat_id:
            self.logger.warn(u"Warning:[create_wxuser][invalid parameters], Detail:[userinfo: {0}, wechat_id: {1}]".format(userinfo, wechat_id))
            raise gen.Return(None)

        yield self.user_wx_user_dao.insert_record(dict(
            is_subscribe=0,
            openid=userinfo.openid,
            nickname=userinfo.nickname,
            sex=userinfo.sex or 0,
            city=userinfo.city,
            country=userinfo.country,
            province=userinfo.province,
            language=userinfo.language,
            headimgurl=userinfo.headimgurl,
            subscribe_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
            wechat_id=wechat_id,
            group_id=0,
            unionid=userinfo.unionid if userinfo.unionid else "",
            source=4
        ))

        ret = yield self.get_wxuser(openid=userinfo.openid, wechat_id=wechat_id)
        raise gen.Return(ret)

    @gen.coroutine
    def update_wxuser(self, userinfo=None, wxuser_id=None):
        if not userinfo or not wxuser_id:
            self.logger.warn(u"Warning:[update_wxuser][invalid parameters], Detail:[userinfo: {0}, wechat_id: {1}]".format(userinfo, wechat_id))
            raise gen.Return(None)

        yield self.user_wx_user_dao.update_by_conds(
            conds={"id": [wxuser_id, "="]},
            fields=dict(
                openid=userinfo.openid,
                nickname=userinfo.nickname,
                sex=userinfo.sex or 0,
                city=userinfo.city,
                country=userinfo.country,
                province=userinfo.province,
                language=userinfo.language,
                headimgurl=userinfo.headimgurl,
                unionid=userinfo.unionid if userinfo.unionid else "",
                source=7
            ))

        ret = yield self.get_wxuser(id=wxuser_id)
        raise gen.Return(ret)

    @gen.coroutine
    def update_wxuser(self, conds=None, fields=None):
        if not conds or not fields:
            self.logger.warn(u"Warning:[update_wxuser][invalid parameters], Detail:[conds: {0}, fields: {1}]".format(
                conds, fields))
            raise gen.Return(None)

        yield self.user_wx_user_dao.update_by_conds(
            conds=conds,
            fields=fields)
        return
