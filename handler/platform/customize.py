# coding=utf-8

# @Time    : 3/3/17 16:03
# @Author  : panda (panyuxin@moseeker.com)
# @File    : customize.py
# @DES     : 各大公司的定制化需求

from tornado import gen

import conf.path as path
import conf.message as msg
from handler.base import BaseHandler
from util.tool.str_tool import email_validate, get_uucode
from util.tool.url_tool import make_url
from util.common import ObjectDict

class CustomizeEDXHandler(BaseHandler):

    '''
    作用：员工代理投递简历
    定制方：e袋洗
    '''

    @gen.coroutine
    def get(self):
        if self.params.emailfriendsent:
            self.render("neo_weixin/sysuser/emailFriendResumeSent.html", params=self.params)
            return
        elif self.params.recom_friend:
            self._get_recom_friend()
            return

    @gen.coroutine
    def _get_recom_friend(self, pid=0, status=0, message=None):

        pid = pid or self.params.pid
        data = ObjectDict({
            'action_url': '/m/custom/edx?recom_friend={}&pid={}'.format(1, pid)
        })

        self.render_page("neo_weixin/sysuser/emailFriendResume.html", data=data, status_code=status, message=message)

    @gen.coroutine
    def post(self):

        if not self.params.name or not email_validate(self.params.email):
            self._get_recom_friend(pid=self.params.pid, status=1, message=msg.CELLPHONE_NAME_EMAIL)
            return

        uucode = get_uucode(lenth=36)

        yield self.customize_ps.create_campaign_email_agentdelivery(params={
            "company_id": self.current_user.company.id,
            "position_id": self.params.pid,
            "employee_id": self.current_user.employee.id,
            "friendname": self.params.name,
            "email": self.params.email,
            "code": uucode,
        })

        # 发送提醒邮件
        # TODO
        # send_recom_friends_notice_to_employee(db=self.db, email=recom_email,
        #                                       company_name=self.current_user.company.abbreviation, code=uucode)

       # 旧模板
        self.redirect(make_url(path.CUSTOMIZE_EDX, self.params, emailfriendsent=1))


