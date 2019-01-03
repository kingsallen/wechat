# coding=utf-8

from tornado import gen

import conf.common as const
import conf.path as path
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated
from util.common.cipher import decode_id


class AnnualSummarizeHandler(BaseHandler):
    """2018年度总结"""
    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):

        self.params.share = self._share()

        return self.render_page(template_name='h5/interpolative/index.html', data=ObjectDict())

    def _share(self):
        default = ObjectDict({
            "cover": self.share_url(self.current_user.company.logo),
            "title": "盘点我的2018内推成就，和我一起穿越时空吧~",
            "description": "感谢内推有你❤",
            "link": self.make_url(path.ANNUAL_SUMMARIZE,
                                  self.params,
                                  transmit=self.position_ps._make_recom(self.current_user.sysuser.id))
        })
        return default


class ApiAnnualSummarizeHandler(BaseHandler):
    """2018年度总结的数据"""
    @handle_response
    @gen.coroutine
    def get(self):
        transmit = self.params.transmit
        trans_user_id = decode_id(transmit) if transmit else self.current_user.sysuser.id
        user_info = yield self.campaign_ps.get_new_year_blessing_user(user_id=trans_user_id)
        data = ObjectDict({
            'jdlist_url': self.make_url(path.POSITION_LIST, self.params, escape=['transmit'], transmit_from=0),
            'bind_url': self.make_url(path.EMPLOYEE_VERIFY, self.params, escape=['transmit'], source=10),  # source=10为通过年度总结引导认证的员工
            'self_summarize_url': self.make_url(path.ANNUAL_SUMMARIZE, self.params, escape=['transmit'])
        })
        if user_info:
            data.update({
                'name': user_info.name,
                'company_name': user_info.company_name,
                'binding_time': user_info.binding_time,
                'employee_count': user_info.employee_count,
                'share_position_count': user_info.share_position_count,
                'viewing_count': user_info.viewing_count,
                'recommend_talent_count': user_info.recommend_talent_count,
                'has_integral_config': user_info.has_integral_config,
                'integrals': user_info.integrals or 0,
                'has_redpacket_activity': user_info.has_redpacket_activity,
                'redpacket_count': user_info.redpacket_count or 0
            })
        self.send_json_success(data=data)


class AnnualSummarizeEntranceHandler(BaseHandler):
    """判断是否用户有年度总结"""
    @handle_response
    @gen.coroutine
    def get(self):
        transmit = self.params.transmit  # transmit代表是他人转发的年度总结，transmit即转发人的user_id
        trans_user_id = decode_id(transmit) if transmit else 0
        has_summarize = False
        if not trans_user_id or int(trans_user_id) == self.current_user.sysuser.id:
            is_self_summarize = True
        else:
            is_self_summarize = False
        user_id = trans_user_id or self.current_user.sysuser.id
        user_info = yield self.campaign_ps.get_new_year_blessing_user(user_id=user_id)
        if user_info:
            has_summarize = True
        is_employee = True if self.current_user.employee else False
        self.send_json_success(ObjectDict(has=has_summarize,
                                          is_employee=is_employee,
                                          is_self_summarize=is_self_summarize))






