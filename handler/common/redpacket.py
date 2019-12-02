# coding=utf-8

from tornado import gen

import conf.common as const
from handler.base import BaseHandler
from util.common import ObjectDict
import conf.message as msg


class RedpacketHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        """打开红包"""
        cardno = self.params.cardno or ''
        id = self.params.id or ''  # 红包id
        rp_info = yield self.redpacket_ps.get_redpacket_info(id, cardno, self.current_user.sysuser.id)
        if rp_info.code == str(const.API_SUCCESS):
            data = rp_info.get("data")
            card = ObjectDict({
                "opened": data.opened,
                "headline": data.headline or msg.RED_PACKET_HEADLINE,
                "headline_failure": data.headline_failure or msg.RED_PACKET_HEADLINE_FAILURE,
                "has_money": data.has_money,
                "redpacket_theme": data.theme or 0
            })
            if data.opened and data.amount is not None:
                card.update(amount=data.amount)
            data = ObjectDict({
                'card': card,
                'cardno': cardno,
                'c_logo': self.static_url(self.current_user.company.logo),
                'username': self.current_user.sysuser.name or self.current_user.sysuser.nickname,
                'company_name': self.current_user.company.abbreviation  # 公司简称
            })
            self.render_page(template_name="adjunct/redpacket.html", data=data)
        else:
            self.render_default_page(kind=1, messages=[rp_info.message])

    @gen.coroutine
    def post(self):
        """领取红包"""
        cardno = self.json_args.cardno or ''
        id = self.json_args.id or ''
        res = yield self.redpacket_ps.open_redpacket(id, cardno, self.current_user.sysuser.id)
        if res.code == str(const.API_SUCCESS):
            self.send_json_success(data=ObjectDict(amount=res.data))
        else:
            self.send_json_error(message=res.message)
