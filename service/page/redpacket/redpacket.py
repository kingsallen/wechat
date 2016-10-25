# coding=utf-8

import os
import time
from hashlib import sha1

import tornado.gen as gen

from service.page.base import PageService
import conf.message as msg


class RedPacketPageService(PageService):

    def __init__(self, logger):
        super().__init__(logger)

    @gen.coroutine
    def __get_card_by_cardno(self, cardno):
        """根据 cardno 获取 scratch card"""
        ret = yield self.hr_hb_scratch_card_ds.get_scratch_card({
            "cardno": cardno
        })
        raise gen.Return(ret)

    @gen.coroutine
    def __make_card_no(self):
        """创建新的 scratch card no"""
        def make_new():
            return sha1('%s%s' % (os.urandom(16), time.time())).hexdigest()
        while True:
            cardno = make_new()
            ret = yield self.__get_card_by_cardno(cardno)
            if ret:
                continue
            else:
                raise gen.Return(cardno)

    @gen.coroutine
    def __create_new_card(self, wechat_id, qx_openid, hr_item_id, amount,
                          hb_config_id, tips):
        """创建新的 scratch card"""
        cardno = yield self.__make_card_no()

        yield self.hr_hb_scratch_card_ds.create_scratch_card({
            "cardno":         cardno,
            "wechat_id":      wechat_id,
            "bagging_openid": qx_openid,
            "hb_item_id":     hr_item_id,
            "amount":         amount,
            "hb_config_id":   hb_config_id,
            "tips":           int(tips)
        })

    # @gen.coroutine
    # def __get_hb_config_by_position(self, position, share_click=False,
    #                                 share_apply=False):
    #     """获取红包配置"""
    #     if not share_click and not share_apply:
    #         raise ValueError(msg.RED_PACKET_TYPE_VALUE_ERROR)
    #
    #     trigger_way = 1 if share_click else 2
    #
    #
    #
    #     sql = """
    #          select hc.*
    #          from hr_hb_config hc
    #          join hr_hb_position_binding hpb
    #          on hpb.hb_config_id = hc.id
    #          where hpb.position_id = {0} and hc.status = 3 and hc.company_id
    #          = {1} and hpb.trigger_way = {2}
    #          """.format(position.id, position.company_id, trigger_way)
    #
    #     return db.get(sql)

    # @gen.coroutine
    # def handle_red_packet_position_related(self, current_user, position,
    #                                        is_click=False, is_apply=False):
    #     """转发类红包触发总入口
    #     """
    #     self.logger.debug(u"[RP]in handle_red_packet_position_related")
    #     assert is_click or is_apply
    #
    #
    #
    #     try:
    #         # 如果 current_user.wxuser 本身就是员工, 不发送红包
    #         if current_user.employee:
    #             self.logger.debug("[RP]当前用户是员工，不触发红包")
    #             return
    #
    #         red_packet_config = None
    #         red_packet_config = self.__get_hongbao_config_by_position(
    #             position, share_click=is_click, share_apply=is_apply)
    #
    #
    #         need_to_send_card = yield self.need_to_send_red_packet_card(
    #             handler, position, is_click=is_click, is_apply=is_apply)
    #
    #         if (need_to_send_card and red_packet_config and
    #                 handler.current_user.recom and
    #                 handler.current_user.wxuser.id and
    #                     handler.PROJECT == const.PROJECT_PLATFORM):
    #
    #             if is_click:
    #                 handler.LOG.debug(u"[RP]转发点击红包开始")
    #             elif is_apply:
    #                 handler.LOG.debug(u"[RP]转发申请红包开始")
    #
    #             handler.LOG.debug(u"[RP]当前点击者 wxuser_id:{},pid:{}".format(
    #                 handler.current_user.wxuser.id, position.id))
    #             last_employee_recom_id = get_referral_employee_wxuser_id(
    #                 handler, handler.current_user.wxuser.id, position.id)
    #             handler.LOG.debug(u"[RP]转发链最近员工 wxuser_id:{}".format(
    #                 last_employee_recom_id))
    #
    #             # 是否同时发给最近员工红包
    #             send_to_employee = (
    #                 last_employee_recom_id and
    #                 last_employee_recom_id != handler.current_user.recom.id)
    #
    #             recom = handler.current_user.recom
    #             recom_wechat = handler.current_user.wechat
    #
    #             ret = yield self.handle_red_packet_card_sending(
    #                 handler, self, red_packet_config, recom, recom_wechat,
    #                 position)
    #             handler.LOG.debug(ret)
    #
    #             if send_to_employee:
    #                 # 同时发红包给最近员工
    #                 employee_wxuser = wxuserDao.get_wxuser_by_wxuser_id(
    #                     self.db, last_employee_recom_id)
    #                 ret = yield self.handle_red_packet_card_sending(
    #                     handler, self, red_packet_config, employee_wxuser,
    #                     recom_wechat,
    #                     position, send_to_employee=True)
    #                 handler.LOG.debug(ret)
    #
    #             if is_click:
    #                 handler.LOG.debug(u"[RP]转发点击红包结束")
    #             elif is_apply:
    #                 handler.LOG.debug(u"[RP]转发申请红包结束")
    #     else:
    #         handler.LOG.debug(u"当前用户是员工, 红包不触发")
    # except Exception, e:
    #     handler.LOG.error(e)

