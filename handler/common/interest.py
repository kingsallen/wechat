# coding=utf-8

from tornado import gen

import conf.common as const
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated, verified_mobile_oneself


class UserCurrentInfoHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """
        返回用户填写的现在公司和现在职位接口

        full 参数用以判断只要返回 bool 就好了还是需要详细的数据
        """

        full = const.YES if int(self.params.full) else const.NO
        result = yield self.user_ps.get_user_user({
            "id": self.current_user.sysuser.id
        })

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

        isfav = const.YES if int(self.params.isfav) else const.NO
        if isfav:
            # 1.添加感兴趣记录
            yield self.user_ps.add_user_fav_position(self.params.pid,
                                                         self.current_user.sysuser.id,
                                                         const.FAV_INTEREST,
                                                         self.current_user.sysuser.mobile,
                                                         self.current_user.wxuser.id,
                                                         self.current_user.recom.id)
            # 2.添加候选人相关记录
            # TODO
            # 3.添加定时任务，若2小时候，没有完善则发送消息模板


    @handle_response
    @authenticated
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
