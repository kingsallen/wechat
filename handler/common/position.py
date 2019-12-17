# coding=utf-8

from tornado import gen

import conf.common as const
import conf.path as path
from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated


class PositionStarHandler(BaseHandler):
    """处理收藏（加星）操作"""

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        try:
            self.guarantee('star', 'pid')
        except:
            raise gen.Return()

        # 收藏操作
        if self.params.star:
            if self.params.employee_id:
                ret = yield self.user_ps.favorite_referral_position(self.current_user.sysuser.id,
                                                                    self.params.employee_id,
                                                                    self.params.pid,
                                                                    self.params.psc)
            else:
                ret = yield self.user_ps.favorite_position(self.current_user.sysuser.id, self.params.pid)
        else:
            ret = yield self.user_ps.unfavorite_position(
                self.current_user.sysuser.id, self.params.pid)

        if ret == 0:
            self.send_json_success()
        else:
            self.send_json_error()


class PositionFavHandler(BaseHandler):
    @handle_response
    @authenticated
    @gen.coroutine
    def get(self, position_id):
        """感兴趣成功"""

        # 诺华定制
        position_info = yield self.position_ps.get_position(position_id, display_locale=self.get_current_locale())
        suppress_apply = self.customize_ps.get_suppress_apply(position_info)
        if suppress_apply.get("is_suppress_apply"):
            self.write_error(404)
            return

        yield self.user_ps.add_user_fav_position(
            position_id,
            self.current_user.sysuser.id,
            const.FAV_INTEREST,
            self.current_user.sysuser.mobile,
            self.current_user.recom.id if self.current_user.recom else 0)

        if not self.current_user.employee:
            yield self.candidate_ps.add_candidate_company(
                self.current_user.sysuser.id,
                self.current_user.sysuser.mobile,
                self.current_user.company.id,
                self.current_user.sysuser.name,
                self.current_user.sysuser.nickname,
                self.current_user.sysuser.email,
                self.current_user.recom.id if self.current_user.recom else 0
            )

        application_url = self.make_url(
            path.APPLICATION,
            self.params,
            pid=position_id,
            escape=['next_url', 'name', 'company', 'position'])

        # 企业号，聚合号职位详情页链接不同
        if self.is_platform:
            position_info_url = self.make_url(
                path.POSITION_PATH.format(position_id),
                self.params,
                escape=['next_url', 'name', 'company', 'position'])
        else:
            position_info_url = self.make_url(
                path.GAMMA_POSITION_HOME.format(position_id),
                self.params,
                escape=['next_url', 'name', 'company', 'position'])

        self.render(template_name="adjunct/interest-success.html",
                    application_url=application_url,
                    position_info_url=position_info_url,
                    suppress_apply=suppress_apply)
