# coding=utf-8

import os
import time
from hashlib import sha1

import tornado.gen as gen

from service.page.base import PageService
import conf.message as msg
import conf.common as const
from setting import settings
import random

from util.common.sharechain import get_referral_employee_wxuser_id, is_1degree_of_employee


class RedpacketPageService(PageService):

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

    @gen.coroutine
    def __get_hb_config_by_position(self, position, share_click=False, share_apply=False):
        """获取红包配置"""
        if not share_click and not share_apply:
            raise ValueError(msg.RED_PACKET_TYPE_VALUE_ERROR)

        trigger_way = 1 if share_click else 2

        config_list = yield self.hr_hb_config_ds.get_hr_hb_config_list({
            "company_id": position.company_id,
            "status": 3
        })

        binding_res = yield self.hr_hb_position_binding_ds.get_hr_hb_position_binding_list({
            "position_id": position.id,
            "trigger_way": trigger_way
        }, fields=['hb_config_id'])
        binding_list = [b.hb_config_id for b in binding_res]

        config = [b for b in config_list if b.id in  binding_list]
        assert len(config) == 1
        raise gen.Return(config[0])


    def __need_to_send(self, current_user, position, is_click=False, is_apply=False):
        """
        检查职位是否正在参与转发点击红包活动
        :param position: 相应职位
        :param is_click: 红包活动类别: 转发点击红包活动
        :param is_apply: 红包活动类别: 转发申请红包活动
        :return: bool
        """
        self.logger.debug("[RP]****************************************")
        # 转发点击和转发申请红包无法同时为 False
        assert is_click or is_apply

        # 校验当前职位是否是属于当前公众号的公司
        if current_user.wechat.company_id != position.company_id:
            self.logger.debug("[RP] position not belong to the wechat.company_id, return False")
            return False

        check_hb_status_passed = False
        if is_click:
            check_hb_status_passed = (
                position.hb_status == const.RP_POSITION_STATUS_CLICK or
                position.hb_status == const.RP_POSITION_STATUS_BOTH)
        elif is_apply:
            check_hb_status_passed = (
                position.hb_status == const.RP_POSITION_STATUS_APPLY or
                position.hb_status == const.RP_POSITION_STATUS_BOTH)
        else:
            self.logger.debug("[RP]something goes wrong")

        self.logger.debug("[RP]current_user.recom.openid:{}".format(current_user.recom.openid))
        self.logger.debug("[RP]current_user.wxuser.id:{}".format(current_user.wxuser.id))
        self.logger.debug("[RP]check_hb_status_passed:{}".format(check_hb_status_passed))
        self.logger.debug("[RP]current_user.recom.id:{}".format(current_user.recom.id))

        ret = bool(current_user.recom.openid and
                   current_user.wxuser.id and
                   check_hb_status_passed and
                   int(current_user.recom.id) != int(current_user.wxuser.id))

        self.logger.debug("[RP]need_to_send_red_packet_card: {}".format(ret))
        self.logger.debug("[RP]****************************************")
        return ret

    @gen.coroutine
    def handle_red_packet_position_related(
        self, current_user, position, is_click=False, is_apply=False):
        """转发类红包触发总入口
        """
        self.logger.debug(u"[RP]in handle_red_packet_position_related")
        assert is_click or is_apply

        try:
            # 如果 current_user.wxuser 本身就是员工, 不发送红包
            if current_user.employee:
                self.logger.debug("[RP]当前用户是员工，不触发红包")
                return

            rp_config = yield self.__get_hb_config_by_position(
                position, share_click=is_click, share_apply=is_apply)

            need_to_send_card = yield self.__need_to_send(
                current_user, position, is_click=is_click, is_apply=is_apply)

            if need_to_send_card and rp_config:
                if is_click:
                    self.logger.debug("[RP]转发点击红包开始")
                elif is_apply:
                    self.logger.debug("[RP]转发申请红包开始")

                self.logger.debug("[RP]当前点击者 wxuser_id:{},pid:{}".format(
                    current_user.wxuser.id, position.id))
                last_employee_recom_id = get_referral_employee_wxuser_id(
                    current_user.wxuser.id, position.id)
                self.logger.debug("[RP]转发链最近员工 wxuser_id:{}".format(
                    last_employee_recom_id))

                # 是否同时发给最近员工红包
                send_to_employee = (
                    last_employee_recom_id and
                    last_employee_recom_id != current_user.recom.id)

                recom = current_user.recom
                recom_wechat = current_user.wechat

                ret = yield self.handle_red_packet_card_sending(
                    current_user, rp_config, recom,
                    recom_wechat, position)
                self.logger.debug(ret)

                if send_to_employee:
                    # 同时发红包给最近员工
                    employee_wxuser = yield self.user_wx_user_ds.get_wxuser({
                        "id": last_employee_recom_id})

                    ret = yield self.handle_red_packet_card_sending(
                        current_user, rp_config, employee_wxuser,
                        recom_wechat, position, send_to_employee=True)
                    self.logger.debug(ret)

                if is_click:
                    self.logger.debug("[RP]转发点击红包结束")
                elif is_apply:
                    self.logger.debug("[RP]转发申请红包结束")
        except Exception as e:
            self.logger.error(e)

    @gen.coroutine
    def handle_red_packet_card_sending(self, current_user, red_packet_config,
                                       recom_wechat, position,
                                       send_to_employee=False):
        """转发类红包发送消息模板
        """
        recom = current_user.recom
        recom_sysuser_id = recom.sysuser_id

        self.logger.debug("[RP]recom_sysuser_id:{}".format(recom_sysuser_id))
        recom_sysuser = yield self.user_user_ds.get_user({
            "id": recom_sysuser_id
        })
        recom_unionid = recom_sysuser.unionid

        self.logger.debug("[RP]recom_unionid:{}".format(recom_unionid))

        recom_qx_wxuser = yield self.user_wx_user_ds.get_wxuser({
            "unionid": recom_unionid,
            "wechat_id": settings['qx_wecaht_id']
        })
        self.logger.debug("[RP]recom_qx_wxuser:{}".format(recom_qx_wxuser))

        nickname = current_user.wxuser.nickname

        # 判断当前用户在这个活动中是否已经为这个受益人发过红包, check 不通过暂停发红包
        malicious_passed = yield self.__checked_maliciousness_passed(
                red_packet_config.id, recom_qx_wxuser.id,
                current_user.wxuser.id)
        if not malicious_passed:
            self.logger.debug(
                "[RP]用户刷单, 红包暂停发送: rp_config_id:{},recom_wxuser_id:{}, wxuser_id:{}"
                .format(red_packet_config.id, recom.id, current_user.wxuser.id))
            raise gen.Return(None)

        # 非员工只能领取一个红包的检查, check 不通过暂停发红包
        non_employee_single_rp_passed = yield self.__non_employee_rp_check_passed(
                red_packet_config.id, recom_wechat, recom.id,
                recom_qx_wxuser.id)
        if not non_employee_single_rp_passed:
            self.logger.debug(
                "[RP]非员工已经领取过红包, 此红包暂停发送: rp_config_id:{},recom_wxuser_id:{}, wxuser_id:{}"
                .format(red_packet_config.id,  recom.id, current_user.wxuser.id))
            raise gen.Return(None)

        # 红包发送对象是否符合配置要求
        matches = yield self.__recom_matches(red_packet_config, recom.openid,
                                             recom_wechat, position)

        if send_to_employee or matches:
            self.logger.debug("[RP]用户是发送红包对象,准备掷骰子")

            throttle_passed = yield self.__check_throttle_passed(
                red_packet_config, recom_qx_wxuser.id, position=position)

            if not throttle_passed:
                self.logger.debug(u"[RP]全局上限验证不通过, 暂停发送")
                raise gen.Return(None)

            self.logger.debug(u"[RP]全局上限验证通过")

            if self.__hit_red_packet(red_packet_config.probability):
                self.logger.debug(u"[RP]掷骰子通过,准备发送红包信封(有金额)")

                # 发送红包消息模版(有金额)
                ret = rp_service.send_red_packet_card(
                    handler,
                    recom.openid,
                    recom_wechat.id,
                    red_packet_config,
                    current_user.wxuser.id,
                    position,
                    nickname=nickname,
                    position_title=position.title,
                    send_to_employee=send_to_employee)
            else:
                # 发送红包消息模版(抽不中)
                self.logger.debug(u"[RP]掷骰子不通过,准备发送红包信封(无金额)")
                ret = rp_service.send_zero_amount_card(
                    handler,
                    recom.openid,
                    recom_wechat.id,
                    red_packet_config,
                    current_user.wxuser.id,
                    nickname=nickname,
                    position_title=position.title,
                    send_to_employee=send_to_employee)

    @gen.coroutine
    def __checked_maliciousness_passed(self, hb_config_id, recom_wxuser_id,
                                     trigger_wxuser_id):
        """查询是否在刷红包 (wxuser_id 配对查重)
        """
        item = yield self.hr_hb_items_ds.get_hb_items({
            "hb_config_id": hb_config_id,
            "wxuser_id": recom_wxuser_id,
            "trigger_wxuser_id": trigger_wxuser_id
        })
        return not item

    @gen.coroutine
    def __non_employee_rp_check_passed(self, hb_config_id, recom_wechat, recom_wxuser_id,
            recom_qx_wxuser_id):
        """
        员工返回 True
        非员工且以前没领过红包返回 True
        非员工且以前领过红包返回 False
        """
        is_employee = yield self.__is_wxuser_employee_of_wechat(recom_wxuser_id,
                                             recom_wechat)
        if is_employee:
            self.logger.debug("[RP]当前红包发送对象是员工,跳过非员工检查红包检查")
            raise gen.Return(True)
        else:
            self.logger.debug("[RP]当前红包发送对象是非员工")
            item = yield self.__get_sent_item_by_qx_wxuser_id(
                hb_config_id, recom_qx_wxuser_id)
            if item:
                self.logger.debug("[RP]当前非员工已经拿过红包")
            else:
                self.logger.debug("[RP]当前非员工没有拿过红包")

            raise gen.Return(not item)

    @gen.coroutine
    def __is_wxuser_employee_of_wechat(self, wxuser_id, wechat):
        """判断wxuser是否是公众号所在公司的员工"""
        employee = yield self.user_employee_ds.get_employee({
            "wxuser_id": wxuser_id,
            "activation": const.OLD_YES,
            "disable": const.NO
        })
        if not employee:
            raise gen.Return(False)
        raise gen.Return(employee.company_id == wechat.company_id)

    @gen.coroutine
    def __get_sent_item_by_qx_wxuser_id(self, hb_config_id, wxuser_id):
        """获取 item"""
        item = yield self.hr_hb_items_ds.get_hb_items({
            "hb_config_id": hb_config_id,
            "wxuser_id": wxuser_id
        })
        raise gen.Return(item)

    @gen.coroutine
    def __recom_matches(self, rp_config, openid, wechat, position):
        """返回 recom 是否符合发送红包对象的要求
        """
        wxuser = yield self.user_wx_user_ds.get_wxuser({
            "openid": openid,
            "wechat_id": wechat.id
        })

        is_employee = yield self.__is_wxuser_employee_of_wechat(wxuser.id, wechat)

        if not wxuser:
            raise gen.Return(False)

        if rp_config.target == const.RED_PACKET_CONFIG_TARGET_FANS:
            raise gen.Return(wxuser and wxuser.is_subscribe)

        elif rp_config.target == const.RED_PACKET_CONFIG_TARGET_EMPLOYEE:
            raise gen.Return(wxuser.employee_id and is_employee)

        elif rp_config.target == const.RED_PACKET_CONFIG_TARGET_EMPLOYEE_1DEGREE:
            if wxuser.employee_id:
                gen.Return(is_employee)
            else:
                gen.Return(is_1degree_of_employee(position.id, wxuser.id))
        else:
            raise ValueError(msg.RED_PACKET_CONFIG_TARGET_VALUE_ERROR)

    @gen.coroutine
    def __check_throttle_passed(self, red_packet_config, wxuser_id,
                              position=None):
        """该用户目前拿到的红包的总金额加上下个红包金额是否超过该公司单次活动金额上限
        """

        # 依赖对仟寻授权
        if wxuser_id is None:
            return True

        # 现在到手的红包总金额
        amount = yield self.__get_amount_sum_config_id_and_wxuser_id(
            red_packet_config.id, wxuser_id)
        current_amount_sum = amount if amount else 0

        # 下一个红包金额
        if position:
            next_red_packet = yield self.__get_next_rp_item(
                red_packet_config.id, red_packet_config.type,
                position_id=position.id)
        else:
            next_red_packet = yield self.__get_next_rp_item(
                red_packet_config.id, red_packet_config.type)

        if next_red_packet is None:
            # 直接返回 True 这样可以在后续发送消息模版之前判断并结束活动
            return True

        next_amount = next_red_packet.amount
        company = yield self.hr_company_ds.get_company({
            "id": red_packet_config.company_id
        })
        hb_throttle = company.hb_throttle

        self.logger.debug(u"[RP]check_throttle_passed?:{}".format(
            float(current_amount_sum) + float(next_amount) <= float(hb_throttle)))

        raise gen.Return(float(current_amount_sum) + float(next_amount) <= float(hb_throttle))

    @gen.coroutine
    def __get_amount_sum_config_id_and_wxuser_id(self, hb_config_id, wxuser_id):
        """返回某人已经在某次活动中获得的金额总数"""
        sent_items = yield self.hr_hb_items_ds.get_hb_items_list(conds={
            "hb_config_id": hb_config_id,
            "wxuser_id": wxuser_id,
        }, fields=["amount"])
        if len(sent_items) == 0:
            raise gen.Return(0)
        raise gen.Return(sum([a.amount for a in sent_items]))

    @gen.coroutine
    def __get_next_rp_item(self, hb_config_id, hb_config_type, position_id=None):
        """获取下个待发红包信息"""
        if ((hb_config_type == const.RED_PACKET_TYPE_SHARE_CLICK or
             hb_config_type == const.RED_PACKET_TYPE_SHARE_APPLY) and
             position_id is not None):

            binding = yield self.hr_hb_position_binding_ds.get_hr_hb_position_binding({
                "hb_config_id": hb_config_id,
                "position_id": position_id
            })
            next_item = yield self.hr_hb_items_ds.get_hb_items({
                "binding_id": binding.id,
                "wxuser_id": 0
            }, appends=["order by index", "limit 1"])

        else:
            next_item = yield self.hr_hb_items_ds.get_hb_items({
                "hb_config_id": hb_config_id,
                "wxuser_id":  0
            }, appends=["order by index", "limit 1"])

        raise gen.Return(next_item)

    @staticmethod
    def __hit_red_packet(probability):
        return probability == 100 or random.uniform(0, 100) < probability

