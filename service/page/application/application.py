# coding=utf-8

import json
from tornado import gen
import conf.common as const
from service.page.base import PageService
from util.common import ObjectDict

class ApplicationPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_application(self, position_id, user_id):
        """返回用户申请的职位"""

        if user_id is None:
            raise gen.Return(ObjectDict())

        ret = yield self.job_application_ds.get_job_application(conds={
            "position_id": position_id,
            "applier_id": user_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_position_applied_cnt(self, conds, fields):
        """返回申请数统计"""

        response = yield self.job_application_ds.get_position_applied_cnt(conds=conds, fields=fields)

        raise gen.Return(response)

    @gen.coroutine
    def is_allowed_apply_position(self, user_id, company_id):
        """获取一个月内该用户再该用户的申请数量
        返回该用户是否可申请该职位
        reference: https://wiki.moseeker.com/application-api.md
        :param user_id: 求职者 id
        :param company_id: 公司 id
        :return:
        {
          'message': '提示信息',
          'status': 0,
          'data': true/false   # ture 表示命中限制，不能投递，false 表示可以投递
        }

        """

        if user_id is None or company_id is None:
            raise gen.Return(True)

        req = ObjectDict({
            'user_id': user_id,
            'company_id': company_id,
        })

        ret = yield self.infra_application_ds.get_application_apply_count(req)
        bool_res = ret.data if ret.status == 0 else True

        raise gen.Return(bool_res)

    @gen.coroutine
    def has_profile(self, user_id):
        """
        判断 user_user 是否有 profile (profile_profile 表数据)
        :param user_id:
        :return:
        """

        has_profile, profile = yield self.infra_profile_ds.has_profile(user_id)
        raise gen.Return((has_profile, profile))

    @gen.coroutine
    def get_app_cv_conf(self, conf_id):
        """
        获得企业申请简历校验配置
        :param user_id:
        :return:
        """

        cv_conf = yield self.hr_app_cv_conf_ds.get_app_cv_conf(conds={
            "id": conf_id,
            "disable": const.NO,
        })
        raise gen.Return(cv_conf)

    @gen.coroutine
    def update_candidate_company(self, name, user_id):
        """
        更新candidate_company表中的name
        :param user_id:
        :return:
        """

        res = yield self.candidate_company_ds.update_candidate_company(
            fields={
                "sys_user_id": user_id
            }, conds={
                "name": name,
            })
        raise gen.Return(res)

    @gen.coroutine
    def custom_check_failure_redirection(self, profile, position):
        """
        处理自定义简历校验和失败后的跳转,
        通用方法, 在 handler 中使用,
        hanlder 调用完此方法后需要立即 return
        """

        cv_conf = yield self.application_ps.get_app_cv_conf(position.app_cv_config_id)
        json_config = json.loads(cv_conf.field_value)

        self.logger.debug("json_confg:{}".format(json_config))

        for c in json_config:
            fields = c.get("fields")
            for field in fields:
                field_name = field.get("field_name")
                required = not field.get("required")
                # 校验失败条件:
                # 1. rquired and
                # 2. field_name 在 profile 对应字端中,但是 profile 中这个字段为空值
                #    or
                #    field_name 是纯自定义字段,但是在 custom_others 中没有这个值
                check_ret = yield self.application_ps.check_custom_field(profile, field_name, self.current_user.sysuser)
                if required and not check_ret:
                    self.logger.debug("自定义字段必填校验错误, 返回app_cv_conf.html\n"
                                      "field_name:{}".format(field_name))
                    # TODO
                    resume_dict = _generate_resume_cv(profile)
                    self.logger.debug("resume_dict: {}".format(resume_dict))

                    raise gen.Return((resume_dict, json_config))

        raise gen.Return((None, None))

    @gen.coroutine
    def check_custom_field(self, profile, field_name, user):
        """
        检查自定义字段必填项
        """

        profile_id = profile.get("profile", {}).get("id", None)
        assert profile_id is not None

        # TODO
        if field_name in cv_profile_keys():
            self.logger.debug("field_name: {}".format(field_name))

            mapping = const.CUSTOM_FIELD_NAME_TO_PROFILE_FIELD[field_name]
            if mapping.startswith("user_user"):

                sysuser_id = profile.get("profile", {}).get("user_id", None)
                if not sysuser_id:
                    return False
                column_name = mapping.split(".")[1]
                self.logger.debug("sysuser_id:{}, column_name:{}".format(sysuser_id, column_name))
                if column_name not in ['email', 'name', 'mobile', 'headimg']:
                    return False
                self.logger.debug("sysuser:{}".format(user))
                return bool(user.__getattr__(column_name))

            if mapping.startswith("profile_education"):
                return bool(profile.get('educations', []))

            if mapping.startswith("profile_workexp"):
                return bool(profile.get('workexps', []))

            if mapping.startswith("profile_projectexp"):
                return bool(profile.get('projectexps', []))

            if mapping.startswith("profile_basic"):
                table_name, column_name = self.__split_dot(mapping)
                key_1 = table_name.split("_")[1]  # should be "basic"
                key_2 = column_name
                return bool(profile.get(key_1, {}).get(key_2, None))

        # TODO
        elif field_name in cv_pure_custom_keys():
            other = get_profile_other_by_profile_id(handler.db, profile_id)

            # 如果存在 other row ,获取 other column
            if other:
                other = other.other
            else:
                return False

            self.logger.debug("other: {}".format(other))
            other_json = json.loads(other)
            self.logger.debug("other_json: {}".format(other_json))

            if not other_json or "null" in other_json:
                return False
            else:
                return bool(other_json.get(field_name))
        else:
            self.logger.error(
                "{} is in neither _cv_profile_keys nor _cv_pure_custom_keys..."
                    .format(field_name)
            )
            return False

    def __split_dot(self, p_str):
        """
        内部方法,不要无故使用
        """
        if p_str.find(".") > 0:
            r_ret = p_str.split(".")
            if len(r_ret) == 2:
                return tuple(r_ret)
        return None
