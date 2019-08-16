# coding=utf-8


import tornado.gen as gen
import conf.path as path
from service.data.base import DataService
from util.tool.http_tool import http_get, http_post_v2, http_get_v2, http_post, http_put_v2, _v2_async_http_post
from conf.newinfra_service_conf.user import user
from conf.newinfra_service_conf.service_info import user_service
from tornado.httputil import url_concat
from setting import settings


class WorkwxDataService(DataService):

    @gen.coroutine
    def create_workwx_user(self, params):
        ret = yield http_put_v2(user.INFRA_GET_WORKWX_USER, user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_workwx_user(self, params):
        ret = yield http_get_v2(user.INFRA_GET_WORKWX_USER, user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_workwx_user_by_sysuser_id(self, params):
        ret = yield http_get_v2(user.INFRA_GET_WORKWX_USER_BY_SYSUSER_ID, user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_workwx(self, params):
        ret = yield http_get(path.COMPANY_GET_WORKWX, jdata=params)
        raise gen.Return(ret)

    @gen.coroutine
    def bind_workwx_qxuser(self, params):
        params.update({"appid": user_service.appid, "interfaceid": user_service.interfaceid}) #post请求参数写在url里面，不能写在body里面
        path = "{0}/{1}{2}".format(settings['cloud'], user_service.service_name, user.INFRA_USER_BIND_WORKWX_QXUSER)
        route = url_concat(path, params)
        ret = yield _v2_async_http_post(route)
        raise gen.Return(ret)

    @gen.coroutine
    def employee_bind(self, sysuser_id, company_id):
        params = {
            "userId": sysuser_id,
            "companyId": company_id,
            "type": 3
        }
        ret = yield http_post(path.INFRA_USER_EMPLOYEE_BIND, jdata=params)
        raise gen.Return(ret)
