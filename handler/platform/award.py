# coding=utf-8

from tornado import gen

import conf.common as const
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated
import time


class ReferralRewardHandler(BaseHandler):
    """红包奖金"""

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        # 获取奖金与红包总数
        params = ObjectDict({
            'page_size': 10,
            'page_num': 1,
            'company_id': self.current_user.company.id,
            'user_id': self.current_user.sysuser.id
        })
        ret = yield self.redpacket_ps.get_redpacket_list(params)
        total_redpacket = ret.total_redpackets
        total_bonus = ret.total_bonus
        self.render_page("employee/bonus-records.html",
                         data=ObjectDict(total_redpacket=total_redpacket,
                                         total_bonus=total_bonus))


class ReferralRedpacketHandler(BaseHandler):
    """红包列表"""

    @handle_response
    @gen.coroutine
    def get(self):
        page_size = int(self.params.get("page_size", 0))
        page_num = int(self.params.get("page_num", 0))
        params = ObjectDict({
            'page_size': page_size,
            'page_num': page_num,
            'company_id': self.current_user.company.id,
            'user_id': self.current_user.sysuser.id
        })
        ret = yield self.redpacket_ps.get_redpacket_list(params)
        list = ret.current_page_data or []
        for i in list:
            i['candidate_name'] = i.get("candidate_name")
            i['position_title'] = i.get("position_title")
            i['open_time'] = i.get("open_time", "")
            i['name'] = self.locale.translate(const.REDPACKET.get(i.get("type")))
            # 认证红包不显示职位和姓名信息
            if i.get("type") == const.RED_PACKET_TYPE_EMPLOYEE_BINDING:
                i['candidate_name'] = ''
                i['position_title'] = ''
            # 转发被点击红包不显示姓名信息
            if i.get("type") == const.RED_PACKET_TYPE_SHARE_CLICK:
                i['candidate_name'] = ''
        total_redpacket = ret.totalRedpackets
        total_bonus = ret.totalBonus
        data = ObjectDict(list=list,
                          total_redpacket=total_redpacket,
                          total_bonus=total_bonus
                          )
        self.send_json_success(data)


class ReferralBonusHandler(BaseHandler):
    """奖金列表"""

    @handle_response
    @gen.coroutine
    def get(self):
        page_size = int(self.params.get("page_size", 0))
        page_num = int(self.params.get("page_num", 0))
        params = ObjectDict({
            'page_size': page_size,
            'page_no': page_num,
            'company_id': self.current_user.company.id
        })
        ret = yield self.user_ps.get_bonus_list(self.current_user.sysuser.id, params)
        list = ret.bonus
        for i in list:
            open_time = time.strftime('%Y-%m-%d', time.localtime(int(i.get("employment_date", 0))/1000))
            i['open_time'] = open_time
            i['type'] = 3  # 入职奖金
            if i.get("cancel"):
                i['type'] = 103  # 取消入职奖金
            i['name'] = self.locale.translate(const.BONUS.get(i.get("type")))
        total_redpacket = ret.total_redpackets
        total_bonus = ret.total_bonus
        data = ObjectDict(list=list,
                          total_redpacket=total_redpacket,
                          total_bonus=total_bonus)
        self.send_json_success(data)


class BonusClaimHandler(BaseHandler):
    """领取奖金"""

    @handle_response
    @gen.coroutine
    def post(self):
        id = self.json_args.get("id")
        ret = yield self.user_ps.claim_bonus(id)
        if ret.status == const.API_SUCCESS:
            self.send_json_success(ret.data)
        else:
            self.send_json_error(message=ret.message)
