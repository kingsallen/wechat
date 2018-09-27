# coding=utf-8

from tornado import gen

import conf.common as const
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated


class ReferralRewardHandler(BaseHandler):
    """红包奖金"""
    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        self.render_page("", data=ObjectDict())


class ReferralRedpacketHandler(BaseHandler):
    """红包列表"""
    @handle_response
    @gen.coroutine
    def get(self):
        page_size = int(self.params.get("page_size", 0))
        page_num = int(self.params.get("page_num", 0))
        params = ObjectDict({
            'page_size': page_size,
            'page_no': page_num
        })
        ret = yield self.user_ps.get_redpacket_list(self.current_user.sysuser.id, params)
        if ret.status == const.API_SUCCESS:
            self.send_json_success(ret.data)
        else:
            self.send_json_error(ret.message)


class ReferralBonusHandler(BaseHandler):
    """红包列表"""
    @handle_response
    @gen.coroutine
    def get(self):
        page_size = int(self.params.get("page_size", 0))
        page_num = int(self.params.get("page_num", 0))
        params = ObjectDict({
            'page_size': page_size,
            'page_no': page_num
        })
        ret = yield self.user_ps.get_bonus_list(self.current_user.sysuser.id, params)
        if ret.status == const.API_SUCCESS:
            self.send_json_success(ret.data)
        else:
            self.send_json_error(ret.message)


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
            self.send_json_error(ret.message)


















