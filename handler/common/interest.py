# coding=utf-8

from tornado import gen

import conf.path as path
import conf.common as const
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated
from util.wechat.template import favposition_notice_to_applier_tpl, favposition_notice_to_hr_tpl
from util.tool.url_tool import make_url


class UserCurrentInfoHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """
        返回用户填写的现在公司和现在职位接口

        full 参数用以判断只要返回 bool 就好了还是需要详细的数据
        """

        full = const.YES if self.params.full else const.NO

        if self.current_user.sysuser:
            if full:
                self.send_json_success(data=ObjectDict(
                    name=self.current_user.sysuser.name,
                    company=self.current_user.sysuser.company,
                    position=self.current_user.sysuser.position
                ))
            else:
                has_info = self.current_user.sysuser.company or self.current_user.sysuser.position
                # 处理感兴趣
                if self.params.isfav:
                    yield self._opt_fav_position(has_info)

                self.send_json_success(
                    data=const.YES if has_info else const.NO)
            return
        else:
            self.send_json_success(data=const.NO)

    @gen.coroutine
    def _opt_fav_position(self, has_info):
        """处理感兴趣后的业务逻辑"""

        if self.params.pid:
            # 1.添加感兴趣记录
            result, _ = yield self.user_ps.add_user_fav_position(
                int(self.params.pid),
                self.current_user.sysuser.id,
                const.FAV_INTEREST,
                self.current_user.sysuser.mobile,
                self.current_user.wxuser.id,
                self.current_user.recom.id if self.params.recom else 0)

            # 2.添加定时任务，若2小时候，没有完善则发送消息模板
            position_info = yield self.position_ps.get_position(self.params.pid)
            real_company_id = yield self.company_ps.get_real_company_id(
                position_info.publisher, position_info.company_id)
            company_info = yield self.company_ps.get_company(
                conds={"id": real_company_id}, need_conf=False)

            link = make_url(path.COLLECT_USERINFO,
                            pid=self.params.pid,
                            source="wx", # 用户前端判断来源
                            wechat_signature=self.current_user.wechat.signature,
                            host=self.request.host)

            if not has_info:
                yield favposition_notice_to_applier_tpl(self.current_user.wechat.company_id,
                                             position_info.title,
                                             company_info.name,
                                             position_info.city,
                                             self.current_user.sysuser.id,
                                             link)

            # 3.添加候选人相关记录
            yield self.candidate_ps.send_candidate_interested(self.current_user.sysuser.id, self.params.pid, 1)

            # 4.向 HR 发送消息模板提示
            if position_info.publisher and result and self.current_user.sysuser.mobile:
                hr_account, hr_wx_user = yield self.position_ps.get_hr_info(position_info.publisher)

                if hr_wx_user:
                    # 4. 向 HR 发送消息模板
                    yield favposition_notice_to_hr_tpl(self.settings.helper_wechat_id,
                                                       hr_wx_user.openid,
                                                       position_info.title,
                                                       self.current_user.sysuser.name or self.current_user.sysuser.nickname,
                                                       self.current_user.sysuser.mobile)
                    return True

        return False

class UserCurrentUpdateHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """更新用户现在公司和现在职位接口
        调整为 get 方式，原因：更新用户信息，需要用户验证手机号，
        此时可能会触发帐号合并，合并完帐号后，需要重新微信 oauth，post 请求无法 oauth
        """

        if not self.params.name or not self.params.company or not self.params.position:
            self.send_json_error()
            return

        self.logger.debug("UserCurrentInfoHandler sysuser_id:{}".format(self.current_user.sysuser.id))
        self.logger.debug("UserCurrentInfoHandler params:{}".format(self.params))

        yield self.user_ps.update_user_user_current_info(
            sysuser_id=self.current_user.sysuser.id,
            data=self.params
        )

        self.send_json_success()
