# coding=utf-8

import tornado.gen as gen

import conf.common as const
import conf.path as path
from service.data.base import DataService
from util.common import ObjectDict
import util.tool.http_tool as http_tool


class InfraProfileDataService(DataService):

    @gen.coroutine
    def get_profile(self, user_id):
        params = ObjectDict(user_id=user_id)
        res = yield http_tool.http_get(path.PROFILE, params)
        return http_tool.unboxing(res)

    @gen.coroutine
    def get_profile_basic(self, profile_id):
        ret = yield self.handle_profile_section(
            {'profile_id': profile_id}, 'get', 'basic')
        return http_tool.unboxing(ret)

    @gen.coroutine
    def update_profile_basic(self, profile_id, basic):
        # TODO tangyiliang 现在自定义简历和常规 profile basic 更新混在一起，最好分开
        params = ObjectDict(
            profile_id=profile_id,
            name=basic.name,
            gender=basic.gender,
        )

        # 调整生日: 老六步生日使用 birthday, 新六步使用 birth
        birth = basic.birthday or basic.birth
        if birth:
            params.update(birth=birth)

        # 自定义简历模版中的字段
        if basic.nationality and basic.nationality.strip():
            params.update(nationality_name=basic.nationality.strip())
        if basic.email and basic.email.strip():
            params.update(email=basic.email.strip())
        if basic.weixin and basic.weixin.strip():
            params.update(weixin=basic.weixin.strip())
        if basic.qq and basic.qq.strip():
            params.update(qq=basic.qq.strip())

        if basic.location:
            basic.city_name = basic.location
            basic.pop('location')
        if basic.city_name is not None:
            params.update(city_name=basic.city_name)

        if basic.remarks:
            basic.self_introduction = basic.remarks
            basic.pop('remarks')
        if basic.self_introduction is not None:
            if basic.self_introduction.strip() == "":
                params.update(self_introduction="")
            else:
                params.update(self_introduction=basic.self_introduction)

        if basic.motto is not None:
            if basic.motto.strip() == "":
                params.update(motto="")
            else:
                params.update(motto=basic.motto)

        self.logger.debug("params:{}".format(params))

        res = yield self.handle_profile_section(
            params, method="update", section="basic")

        return http_tool.unboxing(res)

    @gen.coroutine
    def get_profile_language(self, profile_id):
        res = yield self.handle_profile_section(
            {'profile_id': profile_id}, 'get', 'language')
        return http_tool.unboxing(res)

    @gen.coroutine
    def create_profile_language(self, record, profile_id):
        res = yield self.handle_profile_section({
            "profile_id": profile_id,
            "level":      record.level,
            "name":       record.language.strip()},
            method="create", section="language")
        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_language(self, record, profile_id):
        res = yield self.handle_profile_section({
                "id":         record.id,
                "profile_id": profile_id,
                "level":      record.level,
                "name":       record.language.strip()
            }, method="update", section="language")
        return http_tool.unboxing(res)

    # noinspection PyUnusedLocal
    @gen.coroutine
    def delete_profile_language(self, record, profile_id=None):
        res = yield self.handle_profile_section(
            {"id": record.id}, method="delete", section="language")
        return http_tool.unboxing(res)

    @gen.coroutine
    def handle_profile_section(self, params, method=None, section=None):
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
            response = yield http_tool.http_get(route, params)
        elif method == "create":
            response = yield http_tool.http_post(route, params)
        elif method == "update":
            response = yield http_tool.http_put(route, params)
        elif method == "delete":
            response = yield http_tool.http_delete(route, params)
        else:
            raise Exception('Unknow Exception')
        return response
