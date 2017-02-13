# coding=utf-8

from service.data.base import DataService
import tornado.gen as gen
from util.common import ObjectDict
from conf.path import USER_COMBINE
from util.tool.http_tool import http_get, http_post, http_put, http_delete, http_patch


class InfraUserDataService(DataService):

    @gen.coroutine
    def post_user_wxbindmobile(self, **kwargs):

        params = ObjectDict({
            "unionid": kwargs["unionid"],
            "mobile": kwargs["mobile"],
            "code": kwargs.get("code" "")
        })

        ret = yield http_post(USER_COMBINE, params)

        raise gen.Return(ret)

