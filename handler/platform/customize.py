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
from util.common import ObjectDict

class CustomizeEmailApplyHandler(BaseHandler):

    '''
    作用：员工代理投递简历
    定制方：e袋洗
    '''

    _EMAIL_APPLY_COMPANY = [926]

    @gen.coroutine
    def get(self):
        if self.current_user.wechat.company_id not in self._EMAIL_APPLY_COMPANY:
            self.write_error(404)
            return

        if self.params.emailfriendsent:
            self.render("neo_weixin/sysuser/emailFriendResumeSent.html", params=self.params)
        elif self.params.recom_friend:
            self._get_recom_friend()
        else:
            self.write_error(404)

    @gen.coroutine
    def _get_recom_friend(self, pid=0, status=0, message=None):

        pid = pid or self.params.pid
        data = ObjectDict({
            'action_url': '/m/custom/edx?recom_friend={}&pid={}'.format(1, pid)
        })

        self.render_page("neo_weixin/sysuser/emailFriendResume.html", data=data, status_code=status, message=message)

    @gen.coroutine
    def post(self):

        if self.current_user.wechat.company_id not in self._EMAIL_APPLY_COMPANY:
            self.send_json_error()
            return

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

        self.redirect(self.make_url(path.CUSTOMIZE_EDX, self.params, emailfriendsent=1))


