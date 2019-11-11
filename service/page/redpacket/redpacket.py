# coding=utf-8

import os
import random
import socket
import time
import traceback
import uuid
import xml.dom.minidom as minidom
from datetime import datetime
from hashlib import sha1, md5
from util.common.cache import BaseRedis

import requests
import tornado.gen as gen

import conf.common as const
import conf.message as msg
import conf.path as path
import conf.wechat as const_wechat
import conf.wechat as wx
from conf.common import RP_LOCKED as FIRST_LOCK
from service.page.base import PageService
from service.page.hr.wechat import WechatPageService
from service.page.user.sharechain import SharechainPageService
from service.page.user.user import UserPageService
from service.page.hr.company import CompanyPageService
from service.page.job.position import PositionPageService
from setting import settings
from util.common import ObjectDict
from util.common.decorator import log_core
from util.tool.str_tool import set_literl, trunc, generate_nonce_str, to_bytes, to_str
from util.tool.url_tool import make_url
from util.wechat.template import (
    rp_binding_success_notice_tpl,
    rp_recom_success_notice_tpl,
    rp_transfer_apply_success_notice_tpl,
    rp_transfer_click_success_notice_tpl,
    rp_recom_screen_success_notice_tpl
)
from util.tool.date_tool import curr_now


class RedpacketPageService(PageService):
    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_redpacket_info(self, id, cardno, user_id):
        """获取红包信息"""
        ret = yield self.infra_redpacket_ds.infra_get_redpacket_info({
            "id": id,
            "cardno": cardno,
            "userId": user_id
        })
        return ret

    @gen.coroutine
    def open_redpacket(self, id, cardno, user_id):
        """领取红包"""
        ret = yield self.infra_redpacket_ds.infra_open_redpacket({
            "id": id,
            "cardno": cardno,
            "userId": user_id
        })
        return ret

    @log_core
    @gen.coroutine
    def __get_card_by_cardno(self, cardno):
        """根据 cardno 获取 scratch card"""
        ret = yield self.hr_hb_scratch_card_ds.get_scratch_card({
            "cardno": cardno
        })
        raise gen.Return(ret)

    @log_core
    @gen.coroutine
    def __make_card_no(self):
        """创建新的 scratch card no"""

        def make_new():
            return sha1(to_bytes('%s%s' % (os.urandom(16), time.time()))).hexdigest()

        while True:
            cardno = make_new()
            ret = yield self.__get_card_by_cardno(cardno)
            if ret:
                continue
            else:
                raise gen.Return(cardno)

    @log_core
    @gen.coroutine
    def __create_new_card(self, wechat_id, qx_openid, hb_config_id,
                          hb_item_id=0, amount=0.0):
        """创建新的 scratch card"""
        cardno = yield self.__make_card_no()

        yield self.hr_hb_scratch_card_ds.create_scratch_card({
            "cardno": cardno,
            "wechat_id": wechat_id,
            "bagging_openid": qx_openid,
            "hb_item_id": hb_item_id,
            "amount": amount,
            "hb_config_id": hb_config_id
        })

        ret = yield self.hr_hb_scratch_card_ds.get_scratch_card(conds={
            "cardno": cardno
        })

        raise gen.Return(ret)

    @log_core
    @gen.coroutine
    def __get_hb_config_by_position(self, position, trigger_way):
        """获取红包配置"""
        if not trigger_way:
            raise ValueError(msg.RED_PACKET_TYPE_VALUE_ERROR)

        config_list = yield self.hr_hb_config_ds.get_hr_hb_config_list({
            "company_id": position.company_id,
            "status": const.HB_CONFIG_RUNNING
        })

        binding_res = yield self.hr_hb_position_binding_ds.get_hr_hb_position_binding_list({
            "position_id": position.id,
            "trigger_way": trigger_way
        }, fields=['hb_config_id'])
        binding_list = [b.hb_config_id for b in binding_res]

        config = [b for b in config_list if b.id in binding_list]
        if config:
            raise gen.Return(config[0])
        else:
            raise gen.Return(ObjectDict())

    def __need_to_send(self, current_user, position,
                       trigger_way):
        """
        检查职位是否正在参与转发点击红包活动
        :param position: 相应职位
        :param trigger_way: 红包调用方式
        :return: bool
        """
        # 转发点击和转发申请红包无法同时为 False
        assert trigger_way

        # 校验当前职位是否是属于当前公众号的公司
        if current_user.wechat.company_id != position.company_id:
            self.logger.debug("[RP] position not belong to the wechat.company_id, return False")
            return False

        check_hb_status_passed = False
        self.logger.debug("[RP]position.hb_status: %s" % position.hb_status)
        # 此处改用与运算的方式判断红包类型
        if trigger_way == const.HB_TRIGGER_WAY_CLICK:
            check_hb_status_passed = True if position.hb_status >> const.HB_INDEX_CLICK & 1 else False
        elif trigger_way == const.HB_TRIGGER_WAY_APPLY:
            check_hb_status_passed = True if position.hb_status >> const.HB_INDEX_APPLY & 1 else False
        elif trigger_way == const.HB_TRIGGER_WAY_SCREEN:
            check_hb_status_passed = True if position.hb_status >> const.HB_INDEX_SCREEN & 1 else False
        else:
            self.logger.debug("[RP]something goes wrong")

        self.logger.debug(
            "[RP]check_hb_status_passed: %s" % check_hb_status_passed)

        self.logger.debug('<><><><><><><><><>')
        self.logger.debug('in __need_to_send')
        self.logger.debug(current_user.recom)
        self.logger.debug(current_user.qxuser.id)
        self.logger.debug(check_hb_status_passed)
        self.logger.debug(int(current_user.recom.id) != int(current_user.sysuser.id))
        self.logger.debug('<><><><><><><><><>')

        if trigger_way == const.HB_TRIGGER_WAY_SCREEN:
            ret = bool(current_user.recom and
                       check_hb_status_passed and
                       int(current_user.recom.id) != int(current_user.sysuser.id))
        else:
            ret = bool(current_user.recom and
                       current_user.qxuser.id and
                       check_hb_status_passed and
                       int(current_user.recom.id) != int(current_user.sysuser.id))

        self.logger.debug("[RP]need_to_send_red_packet_card: %s" % ret)
        return ret

    @gen.coroutine
    def handle_red_packet_from_rabbitmq(self, data):
        """通过rabbitmq触发的红包总入口"""

        try:
            hr_company_ps = CompanyPageService()
            user_ps = UserPageService()
            position_ps = PositionPageService()
            redis = BaseRedis()
            user_id = data.get("user_id")
            company_id = data.get("company_id")
            wechat_id = data.get("wechat_id")
            position_id = data.get("position_id", 0)
            be_recom_user_id = data.get("be_recom_user_id", 0)
            direct_referral_user_id = data.get("direct_referral_user_id", 0)
            psc = data.get("psc", 0)
            rp_type = data.get("rp_type")

            if rp_type == const.EMPLOYEE_BIND_RP_TYPE:
                yield self.handle_red_packet_employee_verification(user_id, company_id, redis)
            elif rp_type == const.SCREEN_RP_TYPE:
                # 拼装与session结构相同的current_user以复用相同的红包方法
                wechat = yield self.hr_wx_wechat_ds.get_wechat(conds={
                    "company_id": company_id
                })
                if be_recom_user_id:
                    wxuser = yield self.user_wx_user_ds.get_wxuser(conds={
                        "sysuser_id": be_recom_user_id,
                        "wechat_id": wechat_id
                    })
                    qxuser = yield self.user_wx_user_ds.get_wxuser(conds={
                        "sysuser_id": be_recom_user_id,
                        "wechat_id": settings['qx_wechat_id']
                    })
                else:
                    wxuser = ObjectDict()
                    qxuser = ObjectDict()
                sysuser = yield self.user_user_ds.get_user(conds={
                    "id": be_recom_user_id
                })
                company = yield hr_company_ps.get_company(conds={
                    "id": company_id
                })
                employee = yield user_ps.get_valid_employee_by_user_id(
                    user_id=be_recom_user_id, company_id=company_id)
                recom = yield self.user_user_ds.get_user(conds={
                    "id": direct_referral_user_id
                })
                if position_id:
                    position = yield position_ps.get_position(position_id)
                else:
                    position = ObjectDict()
                current_user = ObjectDict(
                    wechat=wechat,
                    wxuser=wxuser,
                    qxuser=qxuser,
                    sysuser=sysuser,
                    company=company,
                    employee=employee,
                    recom=recom
                )
                self.logger.info("[RP]current_user: {}".format(current_user))
                yield self.handle_red_packet_screen_profile(current_user, position,
                                                            trigger_way=const.HB_TRIGGER_WAY_SCREEN,
                                                            recom_user_id=user_id, psc=psc)
        except Exception as e:
            self.logger.error(traceback.format_exc())

    @gen.coroutine
    def handle_red_packet_employee_verification(self, user_id, company_id, redislocker):
        """对于 user_id, company_id
        发送员工认证红包
        """

        # 先确认公司是否属于集团公司
        belongs_to_group = yield self.infra_company_ds.belongs_to_group_company(company_id)
        if belongs_to_group:
            # 获取集团公司 id 后构建 company_id
            company_list = yield self.infra_company_ds.get_group_company_list(company_id)
            company_ids = [c.id for c in company_list]
        else:
            company_ids = [company_id]

        # 构建一个 SQL where-in 子句
        appends = [" and company_id in %s" % set_literl(company_ids)]

        # 8<------8<------8<------8<------8<------8<------8<------8<------8<---
        # 现在兄弟公司的员工认证红包／推荐红包可以在不同的兄弟公司之间同时开多个（但是每个公司中的该类红包活动同时进行依然只有一个）
        # 集团公司员工拿哪个兄弟公司红包活动的红包 取决于 当前的兄弟公司公司（即当前的微信公众号）
        # 校验红包活动
        rp_config = yield self.hr_hb_config_ds.get_hr_hb_config(
            conds={
                'type': const.RED_PACKET_TYPE_EMPLOYEE_BINDING,
                'status': const.HB_CONFIG_RUNNING,
                'company_id': company_id
            })
        # 8<------8<------8<------8<------8<------8<------8<------8<------8<---

        self.logger.debug("rp_config: %s" % rp_config)

        if not rp_config:
            self.logger.debug('[RP]员工认证红包活动不存在, company_id: %s' % company_id)
            return

        # 复写 company_id 为红包活动的 company_id
        # 因为有可能兄弟公司使用了集团公司内的其他公司的正在进行的红包活动
        company_id = rp_config.company_id

        # 校验员工认证信息
        employee = yield self.user_employee_ds.get_employee(
            conds={
                'sysuser_id': user_id,
                'company_id': company_id,
                'activation': const.OLD_YES,
                'disable': const.OLD_YES,
                'is_rp_sent': const.NO
            }, appends=appends)
        if not employee:
            self.logger.debug(
                '[RP]员工绑定状态不正确, user_id: %s' % user_id)
            return
        # 检验员工是否领取过红包
        employee_ = yield self.user_employee_ds.get_employee(
            conds={
                'sysuser_id': user_id,
                'company_id': company_id,
                'is_rp_sent': const.YES
            }, appends=appends)
        if employee_:
            self.logger.debug(
                '[RP]员工已经领取过红包, user_id: %s' % user_id)
            return

        # 员工认证红包不需要校验上限
        # 为红包处理加 redis 锁
        # 检查红包锁
        rplock_key = const.RP_EMP_LOCK_FMT % (rp_config.id, user_id)
        if redislocker.incr(rplock_key) is FIRST_LOCK:
            self.logger.debug("[RP]红包锁创建成功， rplock_key: %s" % rplock_key)
            company = yield self.hr_company_ds.get_company({'id': company_id})
            company_conf = yield self.hr_company_conf_ds.get_company_conf({'company_id': company_id})
            employee_slug = company_conf.employee_slug or '员工'
            wechat = yield self.hr_wx_wechat_ds.get_wechat({'company_id': company_id})
            qxuser = yield self.user_wx_user_ds.get_wxuser({
                'sysuser_id': user_id, 'wechat_id': settings['qx_wechat_id']
            })

            # 如果是订阅号，那么无法获取 recom_wxuser
            # 将 openid = 0 传递到 __send_red_packet_card， 跳过使用企业号发送消息模版
            recom_wxuser = ObjectDict()
            if wechat.type == const.WECHAT_TYPE_SUBSCRIPTION:  # 如果 wechat 是订阅号
                recom_wxuser.openid = 0
            elif wechat.type == const.WECHAT_TYPE_SERVICE:  # 如果 wechat 是服务号
                recom_wxuser = yield self.user_wx_user_ds.get_wxuser({
                    'sysuser_id': user_id, 'wechat_id': wechat.id
                })
            else:
                assert False  # should not be here

            try:
                if self.__hit_red_packet(rp_config.probability):
                    self.logger.debug("[RP]掷骰子通过,准备发送红包信封(有金额)")

                    # 发送红包消息模版(有金额)
                    yield self.__send_red_packet_card(
                        recom_wxuser.openid,
                        wechat.id,
                        rp_config,
                        qxuser.id,
                        current_qxuser_id=qxuser.id,
                        company_name=company.name,
                        employee_slug=employee_slug
                    )
                else:
                    # 发送红包消息模版(抽不中)
                    self.logger.debug("[RP]掷骰子不通过,准备发送红包信封(无金额)")
                    yield self.__send_zero_amount_card(
                        recom_wxuser.openid,
                        wechat.id,
                        rp_config,
                        qxuser.id,
                        company_name=company.name,
                        employee_slug=employee_slug
                    )

            except Exception as e:
                self.logger.error(e)
            finally:
                # 释放红包锁
                redislocker.delete(rplock_key)
                self.logger.debug("[RP]红包锁释放成功， rplock_key: %s" % rplock_key)
        else:
            self.logger.debug("[RP]触发红包锁，该红包逻辑正在处理中， rplock_key: %s" % rplock_key)

        yield self.user_employee_ds.update_employee(
            conds={'id': employee.id}, fields={'is_rp_sent': const.YES}
        )
        self.logger.debug("[RP]员工认证红包发送成功")

    @log_core
    @gen.coroutine
    def handle_red_packet_recom(self, recom_current_user, recom_record_id, redislocker,
                                realname, position_title):
        """推荐类红包入口"""

        company_id = recom_current_user.company.id

        # 先确认公司是否属于集团公司
        belongs_to_group = yield self.infra_company_ds.belongs_to_group_company(
            company_id)
        if belongs_to_group:
            # 获取集团公司 id 后构建 company_id
            company_list = yield self.infra_company_ds.get_group_company_list(
                company_id)
            company_ids = [c.id for c in company_list]
        else:
            company_ids = [company_id]

        # 构建一个 SQL where-in 子句
        appends = [" and company_id in %s" % set_literl(company_ids)]

        # 8<------8<------8<------8<------8<------8<------8<------8<------8<---
        # 现在兄弟公司的员工认证红包／推荐红包可以在不同的兄弟公司之间同时开多个（但是每个公司中的该类红包活动同时进行依然只有一个）
        # 集团公司员工拿哪个兄弟公司红包活动的红包 取决于 当前的兄弟公司公司（即当前的微信公众号）
        # 校验红包活动
        rp_config = yield self.hr_hb_config_ds.get_hr_hb_config(
            conds={
                'type': const.RED_PACKET_TYPE_RECOM,
                'status': const.HB_CONFIG_RUNNING,
                'company_id': company_id
            })
        # 8<------8<------8<------8<------8<------8<------8<------8<------8<---

        self.logger.debug("rp_config: %s" % rp_config)

        if not rp_config:
            self.logger.debug('[RP]推荐红包活动不存在, company_id: %s' %
                              recom_current_user.company.id)
            return

        # 复写 company_id 为红包活动的 company_id
        # 因为有可能兄弟公司使用了集团公司内的其他公司的正在进行的红包活动
        company_id = rp_config.company_id

        # 校验员工信息
        employee = yield self.user_employee_ds.get_employee(
            conds={
                'sysuser_id': recom_current_user.sysuser.id,
                'activation': const.OLD_YES,
                'disable': const.OLD_YES
            }, appends=appends)

        if not employee:
            self.logger.debug(
                '[RP]员工绑定状态不正确, user_id: %s' % recom_current_user.sysuser.id)
            return

        recom_record = yield self.candidate_recom_record_ds.get_candidate_recom_record(
            {'id': recom_record_id})

        if not recom_record:
            self.logger.debug('[RP]推荐数据不正确, recom_record_id: %s' % recom_record_id)
            return

        self.logger.debug("[RP]推荐红包开始")

        user_id = recom_current_user.sysuser.id
        recom_wechat = recom_current_user.wechat
        recom_wxuser = recom_current_user.wxuser
        recom_qxuser = recom_current_user.qxuser

        # 如果是订阅号，那么无法获取 recom_wxuser
        # 将 openid = 0 传递到 __send_red_packet_card， 跳过使用企业号发送消息模版
        if not recom_wxuser:
            recom_wxuser = ObjectDict()
            recom_wxuser.openid = 0

        self.logger.debug('[RP] company_id: %s' % company_id)
        self.logger.debug('[RP] user_id: %s' % user_id)
        self.logger.debug('[RP] recom_wechat: %s' % recom_wechat)
        self.logger.debug('[RP] recom_wxuser: %s' % recom_wxuser)
        self.logger.debug('[RP] recom_qxuser: %s' % recom_qxuser)

        rplock_key = const.RP_RECOM_LOCK_FMT % (rp_config.id, user_id)
        if redislocker.incr(rplock_key) is FIRST_LOCK:
            self.logger.debug("[RP]红包锁创建成功， rplock_key: %s" % rplock_key)

            try:
                if self.__hit_red_packet(rp_config.probability):
                    self.logger.debug("[RP]掷骰子通过,准备发送红包信封(有金额)")

                    # 发送红包消息模版(有金额)
                    yield self.__send_red_packet_card(
                        recom_wxuser.openid,
                        recom_wechat.id,
                        rp_config,
                        recom_qxuser.id,
                        current_qxuser_id=recom_qxuser.id,
                        position=None,
                        company_name=recom_current_user.company.name,
                        recomee_name=realname,
                        position_title=position_title,
                        recom_qx_user=recom_qxuser,
                        recom_record=recom_record
                    )
                else:
                    # 发送红包消息模版(抽不中)
                    self.logger.debug("[RP]掷骰子不通过,准备发送红包信封(无金额)")
                    yield self.__send_zero_amount_card(
                        recom_wxuser.openid,
                        recom_wechat.id,
                        rp_config,
                        recom_qxuser.id,
                        company_name=recom_current_user.company.name,
                        recomee_name=realname,
                        position_title=position_title,
                        recom_qx_user=recom_qxuser,
                        recom_record=recom_record
                    )

            except Exception as e:
                self.logger.error(e)
            finally:
                # 释放红包锁
                redislocker.delete(rplock_key)
                self.logger.debug("[RP]红包锁释放成功， rplock_key: %s" % rplock_key)
        else:
            self.logger.debug(
                "[RP]触发红包锁，该红包逻辑正在处理中， rplock_key: %s" % rplock_key)

        self.logger.debug("[RP]推荐红包发送成功")

    @log_core
    @gen.coroutine
    def handle_red_packet_screen_profile(self,
                                         current_user,
                                         position,
                                         trigger_way,
                                         recom_user_id,
                                         **kwargs):
        """入职类红包触发总入口"""
        try:
            rp_config = yield self.__get_hb_config_by_position(position=position, trigger_way=trigger_way)
            if not rp_config:
                self.logger.debug("[RP]无红包活动")
                return

            application = yield self.job_application_ds.get_job_application(conds={
                "position_id": position.id,
                "applier_id": current_user.sysuser.id
            })
            if not application:
                self.logger.debug('[RP]申请数据不正确, position: %s,  post_user_id: %s, post_user_id: %s'
                                  % (position.id, recom_user_id, current_user.sysuser.id))
                return

            params = {'position_id': position.id,
                      'presentee_user_id': current_user.sysuser.id}

            # 如果没有recom_user_id, 说明申请不是员工推荐产生的，推荐人为直接推荐人
            if recom_user_id and rp_config.target == const.RED_PACKET_CONFIG_TARGET_EMPLOYEE:
                params.update({'app_id': application.id,
                               'post_user_id': recom_user_id})
            else:
                recom_user_id = current_user.recom.id

            if not recom_user_id:
                self.logger.debug('[RP]推荐数据不正确, position: %s, app_id: %s, presentee_user_id: %s, post_user_id: %s'
                                      % (position.id, application.id, current_user.sysuser.id, recom_user_id))
                return

            recom_record = yield self.candidate_recom_record_ds.get_candidate_recom_record(params)

            # if not recom_record:
            #     self.logger.debug('[RP]推荐数据不正确, position: %s, app_id: %s, presentee_user_id: %s, post_user_id: %s'
            #                       % (position.id, application.id, current_user.sysuser.id, recom_user_id))
            #     return

            need_to_send_card = self.__need_to_send(
                current_user, position, trigger_way)

            if need_to_send_card and rp_config:
                self.logger.debug("[RP]初筛通过红包开始")
            else:
                self.logger.debug("[RP]职位红包数据不正确, position: %s, app_id: %s, presentee_user_id: %s, post_user_id: %s"
                                  % (position.id, application.id, current_user.sysuser.id, recom_user_id))
                return

            user_ps = UserPageService()
            wechat_ps = WechatPageService()
            recom_wechat = current_user.wechat
            recom_user = yield user_ps.get_user_user({
                "id": recom_user_id
            })
            nickname = current_user.sysuser.name or current_user.sysuser.nickname
            recom_qxuser = yield self.user_wx_user_ds.get_wxuser(conds={
                "sysuser_id": recom_user_id,
                "wechat_id": settings['qx_wechat_id']
            })

            # 如果是订阅号，那么无法获取 recom_wxuser
            # 将 openid = 0 传递到 __send_red_packet_card， 跳过使用企业号发送消息模版

            is_service_wechat = recom_wechat.type == 1
            if is_service_wechat:
                recom_wxuser = yield user_ps.get_wxuser_sysuser_id_wechat_id(
                    recom_user_id, recom_wechat.id)

            else:
                recom_wxuser = yield user_ps.get_wxuser_sysuser_id_wechat_id(
                    recom_user_id, settings.qx_wechat_id)
                recom_wechat = yield wechat_ps.get_wechat(
                    {"id": settings.qx_wechat_id})

            self.logger.debug('[RP] user_id: %s' % recom_user_id)
            self.logger.debug('[RP] recom_wechat: %s' % recom_wechat)
            self.logger.debug('[RP] recom_wxuser: %s' % recom_wxuser)
            self.logger.debug('[RP] recom_qxuser: %s' % recom_qxuser)

            # 判断红包是否直接发送给员工一度（这里的逻辑与转发点击和转发申请不同）
            sharechain_ps = SharechainPageService()
            psc = kwargs.get("psc")
            first_degree_id = 0
            if psc:
                is_1degree = yield sharechain_ps.is_employee_presentee(
                    psc)
                if is_1degree:
                    share_chain = yield self.candidate_share_chain_ds.get_share_chain({
                        "id": psc
                    })
                    if share_chain.parent_id:
                        first_degree_id = share_chain.recom_user_id
                    else:
                        first_degree_id = share_chain.presentee_user_id

            self.logger.debug("[RP]first_degree_id: {}".format(first_degree_id))
            send_to_first_degree = (
                first_degree_id and
                first_degree_id != recom_user_id and rp_config.target == const.RED_PACKET_CONFIG_TARGET_EMPLOYEE_1DEGREE)

            if send_to_first_degree:
                self.logger.debug("[RP]发送红包给员工一度")
                recom_user = yield user_ps.get_user_user({
                    "id": first_degree_id
                })

                if is_service_wechat:
                    recom_wxuser = yield user_ps.get_wxuser_sysuser_id_wechat_id(
                        first_degree_id, recom_wechat.id)
                else:
                    recom_wxuser = yield user_ps.get_wxuser_sysuser_id_wechat_id(
                        first_degree_id, settings.qx_wechat_id)
                recom_qxuser = yield self.user_wx_user_ds.get_wxuser(conds={
                    "sysuser_id": first_degree_id,
                    "wechat_id": settings['qx_wechat_id']
                })

            matches = yield self.__recom_matches(
                rp_config, recom_user, recom_wechat, **kwargs)

            if send_to_first_degree or matches:
                self.logger.debug("[RP]用户是发送红包对象,准备掷骰子")

                redislocker = BaseRedis()
                rplock_key = const.ON_BOARD_LOCK_FMT % (rp_config.id, recom_user_id)
                if redislocker.incr(rplock_key) is FIRST_LOCK:
                    self.logger.debug("[RP]红包锁创建成功， rplock_key: %s" % rplock_key)

                    try:
                        if self.__hit_red_packet(rp_config.probability):
                            self.logger.debug("[RP]掷骰子通过,准备发送红包信封(有金额)")

                            # 发送红包消息模版(有金额)
                            yield self.__send_red_packet_card(
                                recom_wxuser.openid,
                                recom_wechat.id,
                                rp_config,
                                recom_qxuser.id,
                                current_qxuser_id=current_user.qxuser.id or 0,
                                position=position,
                                nickname=nickname,
                                position_title=position.title,
                                recom_record=recom_record
                            )
                        else:
                            # 发送红包消息模版(抽不中)
                            self.logger.debug("[RP]掷骰子不通过,准备发送红包信封(无金额)")
                            yield self.__send_zero_amount_card(
                                recom_wxuser.openid,
                                recom_wechat.id,
                                rp_config,
                                current_user.qxuser.id or 0,
                                nickname=nickname,
                                position_title=position.title,
                                recom_record=recom_record
                            )

                    except Exception as e:
                        self.logger.error(e)
                    finally:
                        # 释放红包锁
                        redislocker.delete(rplock_key)
                        self.logger.debug("[RP]红包锁释放成功， rplock_key: %s" % rplock_key)
                else:
                    self.logger.debug(
                        "[RP]触发红包锁，该红包逻辑正在处理中， rplock_key: %s" % rplock_key)

                self.logger.debug("[RP]初筛红包发送成功")

        except Exception as e:
            self.logger.error(traceback.format_exc())

    @log_core
    @gen.coroutine
    def handle_red_packet_position_related(self,
                                           current_user,
                                           position,
                                           redislocker,
                                           is_click=False,
                                           is_apply=False,
                                           **kwargs):
        """转发类红包触发总入口
        """
        assert is_click or is_apply

        try:
            if is_click:
                trigger_way = const.HB_TRIGGER_WAY_CLICK
            else:
                trigger_way = const.HB_TRIGGER_WAY_APPLY
            rp_config = yield self.__get_hb_config_by_position(
                position, trigger_way=trigger_way)
            if not rp_config:
                self.logger.debug("[RP]无红包活动")
                return

            # 如果 current_user.wxuser 本身就是员工, 不发送红包
            if current_user.employee:
                self.logger.debug("[RP]当前用户是员工，不触发红包")
                return

            need_to_send_card = self.__need_to_send(
                current_user, position, trigger_way)

            if need_to_send_card and rp_config:
                self.logger.debug("[RP]转发点击红包开始" if is_click
                                  else "[RP]转发申请红包开始")

                recom = current_user.recom
                recom_wechat = current_user.wechat
                trigger_qxuser_id = current_user.qxuser.id
                trigger_user_id = current_user.sysuser.id

                self.logger.debug("[RP]当前点击者 wxuser_id: %s,pid: %s" %
                                  (current_user.wxuser.id, position.id))

                sharechain_ps = SharechainPageService()
                last_employee_user_id, _ = yield sharechain_ps.get_referral_employee_user_id(
                    trigger_user_id, position.id)

                self.logger.debug("[RP]转发链最近员工 user_id:{}".format(
                    last_employee_user_id))

                user_ps = UserPageService()
                wechat_ps = WechatPageService()

                is_service_wechat = recom_wechat.type == 1
                if is_service_wechat:
                    recom_wxuser = yield user_ps.get_wxuser_sysuser_id_wechat_id(
                        recom.id, recom_wechat.id)

                else:
                    recom_wxuser = yield user_ps.get_wxuser_sysuser_id_wechat_id(
                        recom.id, settings.qx_wechat_id)
                    recom_wechat = yield wechat_ps.get_wechat(
                        {"id": settings.qx_wechat_id})

                # 是否同时发给最近员工红包
                send_to_employee = (
                    last_employee_user_id and
                    last_employee_user_id != current_user.recom.id)

                # 为红包处理加 redis 锁
                # 检查红包锁
                rplock_key = const.RP_POS_LOCK_FMT % (rp_config.id, recom.id, trigger_qxuser_id)
                if redislocker.incr(rplock_key) is FIRST_LOCK:
                    self.logger.debug("[RP]红包锁创建成功， rplock_key: %s" % rplock_key)
                    try:
                        ret = yield self.handle_red_packet_card_sending(
                            current_user,
                            rp_config,
                            recom,
                            recom_wxuser,
                            recom_wechat,
                            position,
                            **kwargs
                        )

                        self.logger.debug(ret)

                        if send_to_employee:
                            last_employee_user = yield user_ps.get_user_user({
                                "id": last_employee_user_id
                            })

                            if is_service_wechat:
                                last_employee_wxuser = yield user_ps.get_wxuser_sysuser_id_wechat_id(
                                    last_employee_user_id, recom_wechat.id)
                            else:
                                last_employee_wxuser = yield user_ps.get_wxuser_sysuser_id_wechat_id(
                                    last_employee_user_id, settings.qx_wechat_id)

                            ret = yield self.handle_red_packet_card_sending(
                                current_user,
                                rp_config,
                                last_employee_user,
                                last_employee_wxuser,
                                recom_wechat,
                                position,
                                send_to_employee=True,
                                **kwargs
                            )

                            self.logger.debug(ret)

                    except Exception as e:
                        self.logger.error(e)
                    finally:
                        # 释放红包锁
                        redislocker.delete(rplock_key)
                        self.logger.debug("[RP]红包锁释放成功， rplock_key: %s" % rplock_key)
                        user_ps = None
                        sharechain_ps = None
                else:
                    self.logger.debug("[RP]触发红包锁，该红包逻辑正在处理中， rplock_key: %s" % rplock_key)

                if is_click:
                    self.logger.debug("[RP]转发点击红包结束")
                elif is_apply:
                    self.logger.debug("[RP]转发申请红包结束")
        except Exception as e:
            self.logger.error(traceback.format_exc())

    @log_core
    @gen.coroutine
    def handle_red_packet_card_sending(self,
                                       current_user,
                                       red_packet_config,
                                       recom_user,
                                       recom_wxuser,
                                       recom_wechat,
                                       position,
                                       send_to_employee=False,
                                       **kwargs):
        """转发类红包发送消息模板
        """

        recom_unionid = recom_user.unionid

        self.logger.debug("[RP]recom_unionid: %s" % recom_unionid)

        recom_qx_wxuser = yield self.user_wx_user_ds.get_wxuser({
            "unionid": recom_unionid,
            "wechat_id": settings['qx_wechat_id']
        })
        self.logger.debug("[RP]recom_qx_wxuser: %s" % recom_qx_wxuser)

        nickname = current_user.sysuser.name or current_user.sysuser.nickname

        # 判断当前用户在这个活动中是否已经为这个受益人发过红包, check 不通过暂停发红包
        malicious_passed = yield self.__checked_maliciousness_passed(
            red_packet_config.id,
            recom_qx_wxuser.id,
            current_user.qxuser.id)

        if not malicious_passed:
            self.logger.debug(
                "[RP]用户刷单, 红包暂停发送: rp_config_id: %s,recom_qx_wxuser: %s, trigger_wxuser_id: %s"
                % (red_packet_config.id, recom_qx_wxuser.id, current_user.qxuser.id))
            raise gen.Return(None)

        # 非员工只能领取一个红包的检查, check 不通过暂停发红包
        non_employee_single_rp_passed = yield self.__non_employee_rp_check_passed(
            red_packet_config, recom_user.id, recom_qx_wxuser.id)

        if not non_employee_single_rp_passed:
            self.logger.debug(
                "[RP]非员工已经领取过红包, 此红包暂停发送: rp_config_id: %s, recom_user.id: %s"
                % (red_packet_config.id, recom_user.id))
            raise gen.Return(None)

        # 红包发送对象是否符合配置要求

        matches = yield self.__recom_matches(
            red_packet_config, recom_user, recom_wechat, **kwargs)

        if send_to_employee or matches:
            self.logger.debug("[RP]用户是发送红包对象,准备掷骰子")

            if self.__hit_red_packet(red_packet_config.probability):
                self.logger.debug("[RP]掷骰子通过,准备发送红包信封(有金额)")

                # 发送红包消息模版(有金额)
                yield self.__send_red_packet_card(
                    recom_openid=recom_wxuser.openid,
                    recom_wechat_id=recom_wechat.id,
                    red_packet_config=red_packet_config,
                    recom_qxuser_id=recom_qx_wxuser.id,
                    current_qxuser_id=current_user.qxuser.id,
                    position=position,
                    nickname=nickname,
                    position_title=position.title,
                    send_to_employee=send_to_employee)
            else:
                # 发送红包消息模版(抽不中)
                self.logger.debug("[RP]掷骰子不通过,准备发送红包信封(无金额)")
                yield self.__send_zero_amount_card(
                    recom_wxuser.openid,
                    recom_wechat.id,
                    red_packet_config,
                    current_user.qxuser.id,
                    nickname=nickname,
                    position_title=position.title,
                    send_to_employee=send_to_employee)

    @log_core
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

    @log_core
    @gen.coroutine
    def __non_employee_rp_check_passed(
        self, hb_config, recom_user_id, recom_qx_wxuser_id):
        """
        员工返回 True
        非员工且以前没领过红包返回 True
        非员工且以前领过红包返回 False
        """
        is_employee = yield self.infra_user_ds.is_valid_employee(
            recom_user_id, hb_config.company_id)
        if is_employee:
            self.logger.debug("[RP]当前红包发送对象是员工,跳过非员工红包检查")
            raise gen.Return(True)
        else:
            self.logger.debug("[RP]当前红包发送对象是非员工")
            item = yield self.__get_sent_item_by_qx_wxuser_id(
                hb_config.id, recom_qx_wxuser_id)
            if item:
                self.logger.debug("[RP]当前非员工已经拿过红包")
            else:
                self.logger.debug("[RP]当前非员工没有拿过红包")

            raise gen.Return(not item)

    @log_core
    @gen.coroutine
    def __get_sent_item_by_qx_wxuser_id(self, hb_config_id, wxuser_id):
        """获取 item"""
        item = yield self.hr_hb_items_ds.get_hb_items({
            "hb_config_id": hb_config_id,
            "wxuser_id": wxuser_id
        })
        raise gen.Return(item)

    @log_core
    @gen.coroutine
    def __recom_matches(self, rp_config, recom_user, wechat, **kwargs):
        """返回 recom 是否符合发送红包对象的要求
        """

        if rp_config.target == const.RED_PACKET_CONFIG_TARGET_FANS:
            if wechat.id == settings.qx_wechat_id:
                wechat_ps = WechatPageService()
                wechat = yield wechat_ps.get_wechat({"company_id": rp_config.company_id})
                wechat_ps = None

            wxuser = yield self.user_wx_user_ds.get_wxuser({
                "unionid": recom_user.unionid,
                "wechat_id": wechat.id
            })
            raise gen.Return(wxuser and wxuser.is_subscribe)

        else:
            is_employee = yield self.infra_user_ds.is_valid_employee(
                recom_user.id, rp_config.company_id)

            if rp_config.target == const.RED_PACKET_CONFIG_TARGET_EMPLOYEE:
                raise gen.Return(is_employee)

            elif rp_config.target == const.RED_PACKET_CONFIG_TARGET_EMPLOYEE_1DEGREE:
                if is_employee:
                    raise gen.Return(True)
                else:
                    sharechain_ps = SharechainPageService()
                    is_1degree = yield sharechain_ps.is_employee_presentee(
                        kwargs.get("psc"))

                    sharechain_ps = None
                    raise gen.Return(is_1degree)

    @log_core
    @gen.coroutine
    def __check_throttle_passed(self, red_packet_config, wxuser_id,
                                next_rp_item):
        """该用户目前拿到的红包的总金额加上下个红包金额是否超过该公司单次活动金额上限
        员工认证红包跳过此检查
        """
        if not wxuser_id:
            return False

        if red_packet_config.type == const.RED_PACKET_TYPE_EMPLOYEE_BINDING:
            return True

        # 现在到手的红包总金额
        amount = yield self.__get_amount_sum_config_id_and_wxuser_id(
            red_packet_config.id, wxuser_id)
        current_amount_sum = amount if amount else 0

        next_amount = next_rp_item.amount
        company_conf = yield self.hr_company_conf_ds.get_company_conf({
            "company_id": red_packet_config.company_id
        })
        hb_throttle = company_conf.hb_throttle

        self.logger.debug("[RP]current_amount_sum: %s" % current_amount_sum)
        self.logger.debug("[RP]next_amount: %s" % next_amount)
        self.logger.debug("[RP]hb_throttle: %s" % hb_throttle)
        ret = float(current_amount_sum) + float(next_amount) <= float(hb_throttle)

        return ret

    @log_core
    @gen.coroutine
    def __get_amount_sum_config_id_and_wxuser_id(self, hb_config_id, wxuser_id):
        """返回某人已经在某次活动中获得的金额总数"""
        sent_items = yield self.hr_hb_items_ds.get_hb_items_list(conds={
            "hb_config_id": hb_config_id,
            "wxuser_id": wxuser_id,
        }, fields=["amount"])
        if len(sent_items) == 0:
            raise gen.Return(0.0)
        else:
            ret = 0.0
            for item in sent_items:
                ret += float(item.amount)

            raise gen.Return(ret)

    @log_core
    @gen.coroutine
    def __get_next_rp_item(self, hb_config_id, hb_config_type, position_id=None):
        """获取下个待发红包信息"""

        if (hb_config_type in [const.RED_PACKET_TYPE_SHARE_CLICK,
                               const.RED_PACKET_TYPE_SHARE_APPLY,
                               const.RED_PACKET_TYPE_SCREEN] and
            position_id):

            binding = yield self.hr_hb_position_binding_ds.get_hr_hb_position_binding({
                "hb_config_id": hb_config_id,
                "position_id": position_id
            })

            next_item = yield self.hr_hb_items_ds.get_hb_items({
                "binding_id": binding.id,
                "wxuser_id": 0
            }, appends=["order by rand()", "limit 1"])

        else:
            next_item = yield self.hr_hb_items_ds.get_hb_items({
                "hb_config_id": hb_config_id,
                "wxuser_id": 0
            }, appends=["order by rand()", "limit 1"])
        return next_item

    @log_core
    @gen.coroutine
    def __update_wxuser_id_into_hb_items(self, qx_openid, current_wxuser_id, rp_item):
        """更新 hb items 写入发送信息"""

        # 此处用乐观锁，将wxuser与红包绑定，保证红包的唯一性
        wxuser = yield self.user_wx_user_ds.get_wxuser({
            "openid": qx_openid,
            "wechat_id": settings['qx_wechat_id']
        })
        current_wxuser_id = current_wxuser_id or 0
        result = yield self.hr_hb_items_ds.update_hb_items(
            conds={
                "id": rp_item.id,
                "wxuser_id": 0
            },
            fields={
                "wxuser_id": wxuser.id,
                "trigger_wxuser_id": current_wxuser_id
            })
        return result

    @staticmethod
    def __hit_red_packet(probability):
        return probability == 100 or random.uniform(0, 100) < probability

    @log_core
    @gen.coroutine
    def __send_red_packet_card(self,
                               recom_openid,
                               recom_wechat_id,
                               red_packet_config,
                               recom_qxuser_id,
                               current_qxuser_id,
                               position=None,
                               **kwargs):
        """发送红包模版消息(有真实金额)
        :param recom_openid:
        :param recom_wechat_id:
        :param red_packet_config:
        :param recom_qxuser_id:
        :param current_qxuser_id:
        :param position: 职位信息
        :return:
        """
        self.logger.debug("*" * 80)

        recom_qx_wxuser = yield self.user_wx_user_ds.get_wxuser(
            conds={'id': recom_qxuser_id})
        recom_qxuser_openid = recom_qx_wxuser.openid

        current_qxuser = yield self.user_wx_user_ds.get_wxuser(
            conds={'id': current_qxuser_id})
        current_qxuser_openid = current_qxuser.openid

        if red_packet_config.type in [0, 1]:
            bagging_openid = current_qxuser_openid
        elif red_packet_config.type in [2, 3, 4]:
            bagging_openid = recom_qxuser_openid
        else:
            assert False  # should not be here

        rp_item = ObjectDict()
        # 防止死循环，此处做次数限制，以现有业务来看，暂定10次已足够
        # todo(niuzneya)10次失败后没有提示，用户依旧会拿不到红包，重构请避免此情况
        num = 10
        while num > 0:
            # 获取下一个待发红包信息
            if position:
                rp_item = yield self.__get_next_rp_item(red_packet_config.id, red_packet_config.type,
                                                        position.id)
            else:
                rp_item = yield self.__get_next_rp_item(red_packet_config.id, red_packet_config.type)

            self.logger.debug("[RP]next rp item: {}".format(rp_item))

            throttle_passed = yield self.__check_throttle_passed(
                red_packet_config, recom_qxuser_id, rp_item)

            if not throttle_passed:
                self.logger.debug(
                    '[RP]throttle上限校验失败, hb_config_id: %s， recom_qxuser_id: %s' % (
                        red_packet_config.id, recom_qxuser_id))
                return
            else:
                self.logger.debug("[RP]全局上限验证通过")

            # 不管用户是否点击拆开了红包
            # 记录当前用户 wxuser_id 和红包获得者 wxuser_id
            result = yield self.__update_wxuser_id_into_hb_items(
                bagging_openid, current_qxuser_id, rp_item)
            if result:
                break
            else:
                self.logger.info("[hb]--用户{}在第{}次获取红包{}失败".format(bagging_openid, 10 - num, rp_item.id))
            num -= 1
            yield gen.sleep(0.5)
        self.logger.debug("用户{}获得红包为{}".format(bagging_openid, rp_item.id))

        recom_record = kwargs.get("recom_record", ObjectDict())
        if recom_record:
            yield self.__bind_recom_record_id2redpacket(recom_record.get("id"), rp_item.id)
            self.logger.debug("职位{}与推荐红包{}绑定".format(recom_record.get("id"), rp_item.id))

        card = yield self.__create_new_card(
            recom_wechat_id, bagging_openid, red_packet_config.id,
            rp_item.id, rp_item.amount)

        self.logger.debug("[RP]红包信封入库成功!")
        self.logger.debug("[RP]准备发送红包信封(有金额)!")
        self.logger.debug("[RP]recom_wechat_id:{}".format(recom_wechat_id))
        recom_wechat = yield self.hr_wx_wechat_ds.get_wechat({
            "id": recom_wechat_id
        })
        self.logger.debug("[RP]recom_wechat:{}".format(recom_wechat))

        self.logger.debug("[RP]将发送模版消息")
        # 发送消息模板
        result = yield self.__send_message_template_with_card_url(
            red_packet_config,
            card,
            recom_openid,
            recom_wechat, **kwargs)

        if result == const.YES:
            # 如果模版消息发送成功
            # 将这张刮刮卡所对应的 hb_item 的状态设置成
            # 发送了消息模成功
            yield self.__update_hb_item_status_with_id(
                rp_item.id,
                to=const.RP_ITEM_STATUS_SENT_WX_MSG_SUCCESS)

        # 因为有金额, 如果没有发送成功，就直接发送红包
        else:
            # 将这张刮刮卡所对应的 hb_item 的状态设置成
            # 发送消息模板失败, 尝试直接发送有金额的红包
            yield self.__update_hb_item_status_with_id(
                rp_item.id,
                to=const.RP_ITEM_STATUS_SENT_WX_MSG_FAILURE)

            self.logger.debug("[RP]使用聚合号发送模版消息失败, 直接发红包")

            rp_sent_ret = yield self.__send_red_packet(
                red_packet_config, recom_wechat.id,
                bagging_openid, card.amount, rp_item.id)

            yield self.__update_hb_scratch_card_status(card.cardno, status=const.SRRATCH_CARD_OPENED)

            self.logger.debug("[RP]直接发送红包后, 将刮刮卡状态置为已打开")

            if rp_sent_ret:
                self.logger.debug("[RP]直接发送红包成功!")

                # 将这张刮刮卡所对应的 hb_item 的状态设置成
                # 跳过发送消息模板后成功发送了红包
                # 同时刷新 open_time
                yield self.__update_hb_item_status_with_id(
                    rp_item.id,
                    to=const.RP_ITEM_STATUS_NO_WX_MSG_MONEY_SENT_SUCCESS,
                    refresh_open_time=True)

            else:
                self.logger.debug("[RP]直接发送红包失败!")

                # 将这张刮刮卡所对应的 hb_item 的状态设置成
                # 跳过模版消息直接发送红包失败
                yield self.__update_hb_item_status_with_id(
                    rp_item.id,
                    to=const.RP_ITEM_STATUS_NO_WX_MSG_MONEY_SEND_FAILURE,
                    refresh_open_time=True)

        # 获取下一个待发红包信息，如果红包发完，关闭红包活动
        if position:
            rp_item = yield self.__get_next_rp_item(red_packet_config.id, red_packet_config.type,
                                                    position.id)
        else:
            rp_item = yield self.__get_next_rp_item(red_packet_config.id, red_packet_config.type)

        self.logger.debug("[RP]next rp item: {}".format(rp_item))

        if not rp_item:
            if position:
                self.logger.debug("[RP]该职位红包已经发完")

                current_hb_status = position.hb_status
                # 更新职位状态至未参与这种类型的红包活动
                yield self.__update_position_hb_status(
                    position.id, current_hb_status,
                    red_packet_config.type)

                remaining_positions = yield self.__get_running_positions_by_config_id(
                    red_packet_config)

                if not remaining_positions:
                    self.logger.debug("[RP]该活动红包已经发完,准备结束活动")
                    yield self.__finish_hb_config(red_packet_config.id)

            else:
                self.logger.debug("[RP]该活动红包已经发完,准备结束活动")
                yield self.__finish_hb_config(red_packet_config.id)

            return

        raise gen.Return(result)

    @log_core
    @gen.coroutine
    def __update_hb_item_status_with_id(self, hb_item_id, to, refresh_open_time=False):
        conds = {"id": hb_item_id}
        fields = {"status": to}
        if refresh_open_time:
            fields.update(open_time=datetime.now())
        yield self.hr_hb_items_ds.update_hb_items(conds=conds, fields=fields)

    @log_core
    @gen.coroutine
    def __update_hb_scratch_card_status(self, cardno, status):
        conds = ObjectDict(cardno=cardno)
        fields = ObjectDict(status=status)
        yield self.hr_hb_scratch_card_ds.update_scratch_card(conds=conds, fields=fields)

    @gen.coroutine
    def __bind_recom_record_id2redpacket(self, cid, hb_item_id):
        yield self.referral_recom_hb_position_ds.create_recom_hb_position(fields={
            "recom_record_id": cid,
            "hb_item_id": hb_item_id
        })

    @log_core
    @gen.coroutine
    def __send_zero_amount_card(
        self, recom_openid, recom_wechat_id, red_packet_config,
        current_qxuser_id, **kwargs):
        """发送红包模版消息(始终是0元)
        """
        qx_wechat = yield self.hr_wx_wechat_ds.get_wechat({
            "id": settings['qx_wechat_id']
        })

        recom_wx_user = yield self.user_wx_user_ds.get_wxuser({
            "openid": recom_openid,
            "wechat_id": recom_wechat_id
        })
        recom_qx_wxuser = yield self.user_wx_user_ds.get_wxuser({
            "unionid": recom_wx_user.unionid,
            "wechat_id": settings['qx_wechat_id']
        })

        # 依赖对仟寻授权
        qx_openid = recom_qx_wxuser.openid

        card = yield self.__create_new_card(recom_wechat_id, qx_openid,
                                            red_packet_config.id)

        self.logger.debug("[RP]红包信封入库成功!")
        self.logger.debug("[RP]准备发送红包信封(0元)!")

        recom_wechat = yield self.hr_wx_wechat_ds.get_wechat({
            "id": recom_wechat_id
        })

        self.logger.debug("[RP]将发送模版消息")
        # 发送消息模板
        result = yield self.__send_message_template_with_card_url(
            red_packet_config, card,
            recom_openid, recom_wechat, **kwargs)

        # 放弃不发(因为本来就没有金额)
        if result == const.NO:
            self.logger.debug("[RP]发送模版消息失败,放弃")

        # 将一个 0 元红包
        # 记录当前用户 wxuser_id 和红包获得者 wxuser_id
        hb_item_id = yield self.__insert_0_amount_sent_history(
            red_packet_config.id, qx_openid, current_qxuser_id)

        # 将新插入的0元红包与刮刮卡绑定
        res = yield self.__bind_0_amount_hb2card(card, hb_item_id)
        if not res:
            self.logger.warning("[RP]0元红包{}与刮刮卡{}绑定失败".format(hb_item_id, card.cardno))

        recom_record = kwargs.get("recom_record", ObjectDict())
        if recom_record:
            yield self.__bind_recom_record_id2redpacket(recom_record.get("id"), hb_item_id)
            self.logger.debug("职位{}与推荐红包{}绑定".format(recom_record.get("id"), hb_item_id))

        raise gen.Return(result)

    @log_core
    @gen.coroutine
    def __update_position_hb_status(self, position_id, current_hb_status, hb_config_type):
        """更新 hb_status 至没有参加当前类型红包活动的状态
        :param position_id: 职位 id
        :param current_hb_status: 现在的 hb_status
        :param hb_config_type: 当前红包活动类型
        :return:
        """
        # 是否正参加活动：
        # 0=未参加  1=正参加点击红包活动  2=正参加被申请红包活动  3=正参加1+2红包活动 以此类推，红包类型为2的次方，采用与运算的方式判断红包类型
        if current_hb_status >> const.HB_CONFIG_TYPR_TO_INDEX[hb_config_type] & 1:
            next_status = current_hb_status - const.HB_CONFIG_TYPR_TO_HB_STATUS[hb_config_type]
        else:

            raise ValueError(msg.RED_PACKET_TYPE_VALUE_ERROR)

        yield self.job_position_ds.update_position(conds={
            "id": position_id
        }, fields={
            "hb_status": next_status
        })

    @log_core
    @gen.coroutine
    def __get_running_positions_by_config_id(self, config):
        """查询这个红包活动中还有没发完红包的职位
        """
        binding_list = yield self.hr_hb_position_binding_ds.get_hr_hb_position_binding_list({
            "hb_config_id": config.id
        })

        if len(binding_list) == 0:
            return None
        else:
            position_ids = [b.position_id for b in binding_list]

        position_list = yield self.job_position_ds.get_positions_list(
            conds=" id in %s" % set_literl(position_ids))

        if position_list:
            position_list = [x for x in position_list if x.hb_status >> const.HB_CONFIG_TYPR_TO_INDEX[config.type] & 1]
            raise gen.Return(position_list)
        else:
            return None

    @log_core
    @gen.coroutine
    def __finish_hb_config(self, hb_config_id):
        """
        标记红包活动结束
        :param hb_config_id: 红包配置id
        :return:
        """
        yield self.hr_hb_config_ds.update_hr_hb_config(
            conds={"id": hb_config_id},
            fields={"status": const.HB_CONFIG_FINISHED}
        )

    @log_core
    @gen.coroutine
    def __send_message_template_with_card_url(
        self, red_packet_config, card, openid, wechat, **kwargs):
        """发送红包的消息模板，根据红包活动的类型发送不同的模板

        模板填充内容在 kwargs 里面，
        先发企业号，失败了就发聚合号
        """
        if not openid or wechat.type == const.WECHAT_TYPE_SUBSCRIPTION:
            return const.NO

        config_type = red_packet_config.type

        card_url = make_url(
            path.RED_PACKET_CARD, {},
            host=settings['m_host'],
            m="new",
            cardno=card.cardno)

        wechat_id1 = wechat.get("id", None)
        wechat_id2 = wechat.get("wechat_id", None)
        assert wechat_id1 or wechat_id2
        wechat_id = wechat_id1 if wechat_id1 else wechat_id2

        if config_type == const.RED_PACKET_TYPE_EMPLOYEE_BINDING:
            assert kwargs.get("company_name") is not None
            assert kwargs.get("employee_slug") is not None

            res = yield rp_binding_success_notice_tpl(
                wechat_id=wechat_id,
                openid=openid,
                link=card_url,
                company_name=kwargs.get("company_name", ""),
                employee_slug=kwargs.get("employee_slug")
            )

        elif config_type == const.RED_PACKET_TYPE_RECOM:
            res = yield rp_recom_success_notice_tpl(
                wechat_id=wechat_id,
                openid=openid,
                link=card_url,
                company_name=kwargs.get("company_name", ""),
                recomee_name=kwargs.get("recomee_name", ""),
                position_title=kwargs.get("position_title", "")
            )

        elif config_type == const.RED_PACKET_TYPE_SHARE_CLICK:
            res = yield rp_transfer_click_success_notice_tpl(
                wechat_id=wechat_id,
                openid=openid,
                link=card_url,
                nickname=kwargs.get("nickname", ""),
                position_title=kwargs.get("position_title", "")
            )

        elif config_type == const.RED_PACKET_TYPE_SHARE_APPLY:
            res = yield rp_transfer_apply_success_notice_tpl(
                wechat_id=wechat_id,
                openid=openid,
                link=card_url,
                nickname=kwargs.get("nickname", ""),
                position_title=kwargs.get("position_title", "")
            )
        elif config_type == const.RED_PACKET_TYPE_SCREEN:
            res = yield rp_recom_screen_success_notice_tpl(
                wechat_id=wechat_id,
                openid=openid,
                link=card_url,
                nickname=kwargs.get("nickname", ""),
                position_title=kwargs.get("position_title", "")
            )
        else:
            raise ValueError(msg.RED_PACKET_TYPE_VALUE_ERROR)

        raise gen.Return(res)

    @log_core
    @gen.coroutine
    def __insert_0_amount_sent_history(self, hb_config_id, recom_qx_openid,
                                       trigger_qx_user_id):
        """
        插入 0 元已经发送的红包数据, 主要用户后期查询存在重复的发送记录,
        而不发送新红包
        """

        recom_qx_user = yield self.user_wx_user_ds.get_wxuser({
            "openid": recom_qx_openid,
            "wechat_id": settings['qx_wechat_id']
        })
        item_id = yield self.hr_hb_items_ds.create_hb_items(fields={
            "hb_config_id": hb_config_id,
            "binding_id": 0,
            "status": const.RP_ITEM_STATUS_ZERO_AMOUNT_WX_MSG_SENT,
            "wxuser_id": recom_qx_user.id,
            "trigger_wxuser_id": trigger_qx_user_id
        })
        return item_id

    @log_core
    @gen.coroutine
    def __send_red_packet(self, rp_config, wechat_id, openid, amount, hb_item_id):
        """
        直接发送红包到用户
        """

        wechat = yield self.hr_wx_wechat_ds.get_wechat({
            "id": wechat_id
        })

        company = yield self.hr_company_ds.get_company({
            "id": rp_config.company_id
        })

        company_abb = company.abbreviation

        if not company_abb:
            company_abb = ""
        else:
            company_abb = trunc(company_abb, limit=20)

        rptype = rp_config.type

        apikey = settings['apikey']
        cert_file_path = settings['cert_file_path']
        key_file_path = settings['key_file_path']

        if rptype == const.RED_PACKET_TYPE_EMPLOYEE_BINDING:
            act_name = "员工认证红包"
            remark = "{0}员工认证红包活动".format(company_abb)
        elif rptype in [const.RED_PACKET_TYPE_RECOM,
                        const.RED_PACKET_TYPE_SHARE_CLICK,
                        const.RED_PACKET_TYPE_SHARE_APPLY,
                        const.RED_PACKET_TYPE_SCREEN]:
            act_name = "职位推荐红包"
            remark = "{0}职位推荐红包活动".format(company_abb)
        else:
            raise ValueError

        amount = int(amount * 1000 / 10)  # 发送单位为分, int类型可能会出错，做一次运算消除误差
        if amount > 1 and act_name is not None and remark is not None:
            qx_openid = openid

            qx_wechat_pay = {
                "appid": settings['wechat_pay_appid'],
                "mch_id": settings['wechat_pay_mchid']
            }

            self.logger.debug("[RP]qx_wechat_pay:{}".format(qx_wechat_pay))

            rp_req_dict = self.__generate_red_packet_dict(
                qx_wechat_pay, qx_openid, amount, send_name=company_abb,
                remark=remark, act_name=act_name, apikey=apikey)

            self.logger.debug("[RP]rp_req_dict:{}".format(rp_req_dict))

            rp_req_xml = self.__to_xml(rp_req_dict)
            self.logger.debug("[RP]rp_req_xml:{}".format(rp_req_xml))

            self.logger.debug("[RP]send RED PACKET to weixin Server")
            res = self.__upload_to_server(
                rp_req_xml, cert_file_path, key_file_path)

            res = to_str(res)
            self.logger.debug("[RP]发送红包结果 res: {}".format(res))

            # 记录红包发送结果
            yield self.__insert_red_packet_sent_record(self.__xml_to_dict(res), hb_item_id)

            return "FAIL" not in res

        else:
            return False

    @staticmethod
    def __make_billno(mch_id):
        """创建微信支付订单号"""
        return (mch_id + datetime.now().strftime("%Y%m%d") +
                str(uuid.uuid1().int)[:10])

    def __generate_red_packet_dict(self, qx_wechat_pay, openid, total_amount,
                                   **kwargs):
        """
        生成包含发送红包信息的 dict
        """
        red_packet_dict = {}

        red_packet_dict.update({
            'nonce_str': generate_nonce_str(),
            'wxappid': qx_wechat_pay['appid'],
            'mch_id': qx_wechat_pay['mch_id'],
            'act_name': kwargs.get("act_name", '仟寻'),
            'send_name': kwargs.get("send_name", '仟寻'),
            'wishing': msg.RED_PACKET_WISHING,
            'remark': kwargs.get("remark", '仟寻红包活动'),
            'mch_billno': self.__make_billno(qx_wechat_pay['mch_id']),
            'total_amount': total_amount,
            'total_num': kwargs.get("total_num", 1),
            'client_ip': socket.gethostbyname(kwargs.get("host", "qx.moseeker.com")),
            're_openid': openid,
            'key': kwargs.get("apikey"),
        })

        siganature = self.__generate_sign(red_packet_dict)
        red_packet_dict.update({
            'sign': siganature
        })

        return red_packet_dict

    @staticmethod
    def __generate_sign(d):
        """
        按照微信支付 api 规则生成 sign
        :param d:
        :return:
        """
        pre_sign = '&'.join(["{}={}".format(k, d[k]) for k in sorted(d) if
                             k != "key"]) + "&key={}".format(d.get('key'))
        return md5(to_bytes(pre_sign)).hexdigest().upper()

    @staticmethod
    def __to_xml(d):
        """
        将 dict 数据合成 post 方法的 xml content
        """
        return const_wechat.WX_SEND_RP_REQUEST_FORMAT.format(
            sign=d['sign'],
            mch_billno=d['mch_billno'],
            mch_id=d['mch_id'],
            wxappid=d['wxappid'],
            send_name=d['send_name'],
            re_openid=d['re_openid'],
            total_amount=d['total_amount'],
            total_num=d['total_num'],
            wishing=d['wishing'],
            client_ip=d['client_ip'],
            act_name=d['act_name'],
            remark=d['remark'],
            nonce_str=d['nonce_str'])

    @staticmethod
    def __upload_to_server(xml_content, cert_file_path, key_file_path):
        """
        向微信服务器发送红包请求
        :param xml_content: xml 数据
        :param cert_file_path: cert 文件
        :param key_file_path: key 文件
        :return: 腾讯服务器返回的内容
            https://pay.weixin.qq.com/wiki/doc/api/cash_coupon.php?chapter=13_5
        """
        url = wx.API_PAY_HONGBAO
        cert = (cert_file_path, key_file_path)
        r = requests.post(url, data=xml_content.encode("utf-8"), cert=cert,
                          verify=False)
        return r.content

    @staticmethod
    def __xml_to_dict(xml_text):
        """
        将微信含有 CDATA 的返回 xml 转换成 dict
        :param xml_text:
        :return:
        """
        doc = minidom.parseString(xml_text)
        ret = {}
        xml_root = doc.childNodes[0]
        for node in xml_root.childNodes:
            if hasattr(node, 'tagName'):
                ret.update({node.tagName: node.childNodes[0].data})
        return ret

    @log_core
    @gen.coroutine
    def __insert_red_packet_sent_record(self, args_dict, hb_item_id):
        """插入红包发送记录"""
        yield self.hr_hb_send_record_ds.insert_record({
            "return_code": args_dict.get('return_code', ''),
            "return_msg": args_dict.get('return_msg', ''),
            "sign": args_dict.get('sign', ''),
            "result_code": args_dict.get('result_code', ''),
            "err_code": args_dict.get('err_code', ''),
            "err_code_des": args_dict.get('err_code_res', ''),
            "mch_billno": args_dict.get('mch_billno', ''),
            "mch_id": args_dict.get('mch_id', ''),
            "wxappid": args_dict.get('wxappid', ''),
            "re_openid": args_dict.get('re_openid', ''),
            "total_amount": int(args_dict.get('total_amount', '0')),
            "send_time": args_dict.get('send_time', ''),
            "send_listid": args_dict.get('send_listid', ''),
            "hb_item_id": hb_item_id
        })

    @log_core
    @gen.coroutine
    def get_last_running_hongbao_config_by_position(self, position_id):
        """
        获取一个职位正在进行的红包活动
        """

        share_info = yield self.infra_redpacket_ds.infra_get_rp_position_share_info(
            {
                "positionId": position_id
            }
        )
        raise gen.Return(share_info.data)

    @log_core
    @gen.coroutine
    def get_position_title_by_recom_record_id(self, recom_record_id):
        ret = ''
        try:
            recom_record = yield self.candidate_recom_record_ds.get_candidate_recom_record({'id': recom_record_id})
            position_id = recom_record.position_id
            position = yield self.job_position_ds.get_position({'id': position_id})
            ret = position.title
        except AttributeError as e:
            self.logger.error(e)
        finally:
            return ret

    @log_core
    @gen.coroutine
    def __bind_0_amount_hb2card(self, card, hb_item_id):
        conds = ObjectDict(cardno=card.cardno)
        fields = ObjectDict(hb_item_id=hb_item_id)
        result = yield self.hr_hb_scratch_card_ds.update_scratch_card(conds=conds, fields=fields)
        return result
