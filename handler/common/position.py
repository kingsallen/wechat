# coding=utf-8

from tornado import gen

import conf.path as path
from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated, verified_mobile_oneself
from util.tool.url_tool import make_url

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
            ret = yield self.user_ps.favorite_position(
                self.current_user, self.params.pid)
        else:
            ret = yield self.user_ps.unfavorite_position(
                self.current_user, self.params.pid)

        if ret:
            self.send_json_success()
        else:
            self.send_json_error()

class PositionFavHandler(BaseHandler):

    @handle_response
    @verified_mobile_oneself
    @authenticated
    @gen.coroutine
    def get(self):
        """感兴趣成功"""



        application_url = make_url(path.APPLICATION+"/app", self.params, escape=['next_url', 'name', 'company', 'position'])
        position_info_url = make_url(path.POSITION_PATH.format(self.params.pid), self.params, escape=['next_url', 'name', 'company', 'position'])

        self.render("weixin/sysuser/interest-success.html",
                    application_url=application_url,
                    position_info_url=position_info_url)

