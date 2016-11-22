# -*- coding=utf-8 -*-

from tornado import gen

import conf.common as const
from handler.base import BaseHandler
from util.common import ObjectDict


class UserCurrentInfoHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        """返回用户填写的现在公司和现在职位接口

        full 参数用以判断只要返回 bool 就好了还是需要详细的数据
        """

        full = const.YES if int(self.params.full) else const.NO
        result = yield self.user_ps.get_user_user_id(
            self.current_user.sysuser.id)

        if result:
            if full:
                self.send_json_success(data=ObjectDict(
                    name=result.name,
                    company=result.company,
                    position=result.position
                ))
            else:
                has_info = result.company or result.position
                self.send_json_success(
                    data=const.YES if has_info else const.NO)
        else:
            self.send_json_success(data=const.NO)

    @gen.coroutine
    def post(self):
        """更新用户现在公司和现在职位接口
        """
        try:
            self.guarantee('name', 'company', 'position')
        except:
            return

        yield self.user_ps.update_user_user_current_info(
            sysuser_id=self.current_user.sysuser.id,
            data=self.params
        )

        self.send_json_success()
