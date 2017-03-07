# coding=utf-8

import tornado.gen as gen

from service.page.base import PageService
import conf.common as const
import conf.path as path
from util.common import ObjectDict
from util.tool.http_tool import http_get, http_post


class ProfilePageService(PageService):
    """对接profile服务
    referer: https://wiki.moseeker.com/profile-api.md
    """

    FE_ROUTES = ObjectDict({
        "basic":          "basic",
        "description":    "basic",
        "jobexp":         "workexp",
        "projectexp":     "projectexp",
        "jobpref":        "intention",
        "language":       "language",
        "skill":          "skill",
        "cert":           "credentials",
        "link":           "works",
        "prize":          "awards",
        "eduexp":         "education",
        "jobexp_company": "jobexp_company"
    })

    BASIC_KEYS = [
        'name', 'birth', 'city_name', 'gender', 'motto', 'self_introduction',
        'profile_id'
    ]

    LANGUAGE_KEYS = [
        'id', 'name', 'level'
    ]

    CERT_KEYS = _SKILL_KEYS = [
        'id', 'name'
    ]

    WORKEXP_KEYS = [
        "id", "start_date", "end_date", "end_until_now", "department_name",
        "job", "description", "company_name"
    ]

    EDU_KEYS = [
        "id", "start_date", "end_date", "end_until_now", "college_name",
        "major_name", "degree", "description", "logo"
    ]

    PROJECTEXP_KEYS = [
        "id", "start_date", "end_date", "end_until_now", "name",
        "company_name", "description"
    ]

    AWARDS_KEYS = [
        "id", "reward_date", "name"
    ]

    WORKS_KEYS = [
        "id", "cover", "url", "description"
    ]

    INTENTION_KEYS = [
        "id", "city_name", "worktype", "position_name", "salary_code"
    ]

    @gen.coroutine
    def has_profile(self, user_id):
        """
        判断 user_user 是否有 profile (profile_profile 表数据)
        :param user_id:
        :return: tuple (bool, profile or None)

        调用方式:
        profile = has_profile[1]
        """

        result, profile = yield self.infra_profile_ds.get_profile(user_id)
        return result, profile

    @gen.coroutine
    def get_profile_basic(self, profile_id):
        result, data = yield self.infra_profile_ds.get_profile_basic(
            profile_id)
        return result, data

    @gen.coroutine
    def update_profile_basic(self, profile_id, params):
        result, data = yield self.infra_profile_ds.update_profile_basic(
            profile_id, params)
        return result, data

    @gen.coroutine
    def get_profile_language(self, profile_id):
        result, data = yield self.infra_profile_ds.get_profile_language(
            profile_id)
        return result, data

    @gen.coroutine
    def create_profile_language(self, record, profile_id):
        result, data = yield self.infra_profile_ds.create_profile_language(
            record, profile_id)
        return result, data

    @gen.coroutine
    def update_profile_language(self, record, profile_id):
        result, data = yield self.infra_profile_ds.update_profile_language(
            record, profile_id)
        return result, data

    @gen.coroutine
    def delete_profile_language(self, record, profile_id):
        result, data = yield self.infra_profile_ds.delete_profile_language(
            record, profile_id)
        return result, data
