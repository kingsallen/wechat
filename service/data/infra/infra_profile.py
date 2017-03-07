# coding=utf-8

import tornado.gen as gen

import conf.common as const
import conf.path as path
from service.data.base import DataService
from util.common import ObjectDict
from util.tool.http_tool import http_get, http_post, http_put, http_delete


class InfraProfileDataService(DataService):

    @gen.coroutine
    def get_profile(self, user_id):
        params = ObjectDict(user_id=user_id)
        response = yield http_get(path.PROFILE, params)
        return response

    # TODO (tangyiliang)
    # @gen.coroutine
    # def import_profile(self, source, username, password, user_id):
    #     params = ObjectDict(
    #         type=int(source),
    #         username=username,
    #         password=password,
    #         user_id=int(user_id))
    #     res = yield self._import_profile(params)
    #     return res
    #
    # @gen.coroutine
    # def import_profile(self, params):
    #     response = yield http_post(path.PROFILE_IMPORT, params)
    #     return response

    @gen.coroutine
    def _handle_profile_section(self, params, method=None, section=None):
        """修改 profile 部分数据的底层方法，
        对应CRUD的method参数为 get, create, update, delete
        对应的 HTTP 动词为 GET, POST, PUT, DELETE

        profile 部分标记字符串 (大小写不限)：
        BASIC
        LANGUAGE
        SKILL
        CREDENTIALS
        EDUCATION
        PROFILE
        WORKEXP
        PROJECTEXP
        AWARDS
        WORKS
        INTENTION
        """
        try:
            if not method or not section:
                raise ValueError
            assert method in ['get', 'create', 'update', 'delete']
            route = getattr(path, ("profile" + section).upper())
        except:
            raise ValueError('Invalid method or section')

        if method == "get":
            response = yield http_get(route, params)
        elif method == "create":
            response = yield http_post(route, params)
        elif method == "update":
            response = yield http_put(route, params)
        elif method == "delete":
            response = yield http_delete(route, params)
        else:
            raise Exception('Unknow Exception')
        return response
