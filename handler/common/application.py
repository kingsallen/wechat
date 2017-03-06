# coding=utf-8

# @Time    : 3/6/17 10:55
# @Author  : panda (panyuxin@moseeker.com)
# @File    : application.py
# @DES     :

import json
from tornado import gen

import conf.common as const
import conf.message as msg

from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated
from util.tool.json_tool import encode_json_dumps
from util.tool.url_tool import make_url

class ApplicationHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self, method):
        try:
            # 重置 event，准确描述
            self._event = self._event + method
            yield getattr(self, 'get_' + method)()
        except Exception as e:
            self.write_error(404)

    @handle_response
    @authenticated
    @gen.coroutine
    def get_app(self):

        position = yield self.position_ps.get_position(self.params.pid)
        # 确认职位是否存在
        if not position:
            self.write_error(404)
            return

        # 判断 current_user 的 profile 是否符合要求
        # 1. 获取 profile
        has_profile, profile = yield self.applicaion_ps.has_profile(self.current_user.sysuser.id)

        # 2. 如果没有 profile 按照规则跳转
        if not has_profile:
            # TODO
            no_profile_redirection(self.params.pid)
            return

        # 3. 如果有 profile 但是是自定义职位,
        #    检查该 profile 是否符合自定义简历必填项,
        #        如果不符合的话跳转到自定义简历填写页
        if position.app_cv_config_id:
            resume_dict, json_config = yield self._custom_check_failure_redirection(profile, position)
            if json_config:
                self.render('weixin/application/app_cv_conf.html',
                            resume=encode_json_dumps(resume_dict),
                            cv_conf=encode_json_dumps(json_config))
                return

        # 定制化需求
        # 雅诗兰黛直接投递
        is_esteelauder = yield self.customize_ps.create_esteelauder_apply(position.company_id, position.app_cv_config_id)
        is_skip = "1" if is_esteelauder else "0"

        # 跳转到 profile get_view, 传递 apply 和 pid
        # TODO
        self.redirect(make_url(const.PROFILE_URL, self.params,
                               apply="1", is_skip=is_skip))

    @gen.coroutine
    def _custom_check_failure_redirection(self, profile, position):
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



