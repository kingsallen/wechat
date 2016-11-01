# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.13

"""

import conf.common as const

from tornado import gen
from handler.base import BaseHandler


class CellphoneBindHandler(BaseHandler):
    """ 发送短信验证码的共通方法
    Referenced Document: https://wiki.moseeker.com/user_account_api.md
                         Point 32, 33
    """

    @gen.coroutine
    def get(self):
        result = yield self.cellphone_ps.send_valid_code(
            self.params.get('mobile', None),
            self.app_id
        )
        if result.status != const.API_SUCCESS:
            self.send_json_error(message=result.message)
        else:
            self.send_json_success()

    @gen.coroutine
    def post(self):
        """校验短信验证码
        必要时合并账号并清空 cookie
        """
        try:
            self.guarantee('mobile', 'code')
        except:
            return

        # 验证手机号
        response = yield self.cellphone_ps.verify_mobile(
            params=self.params,
            app_id=self.app_id
        )

        # 更新数据库
        if response.status != const.API_SUCCESS:
            self.send_json_error(message=response.message)
            return
        else:
            yield self.user_ps.bind_mobile(self.current_user.sysuser.id,
                                           self.params.mobile)

        # 检查是否需要合并 pc 账号
        response = yield self.cellphone_ps.wx_pc_combine(
            mobile=self.params.mobile,
            unionid=self.current_user.sysuser.unionid,
            app_id=self.app_id
        )

        if response.status != const.API_SUCCESS:
            self.send_json_error(message=response.message)
            return
        else:
            ret_user_id = response.data.id
            if str(ret_user_id) != str(self.current_user.sysuser.id):
                self.clear_cookie(name=const.COOKIE_SESSIONID)
            self.send_json_success()
