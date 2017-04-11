# coding=utf-8

"""
挖掘被动求职者相关的 Handler
"""

import tornado.gen
from handler.base import BaseHandler

import conf.message as msg
from util.tool.date_tool import curr_now_dateonly
import conf.common as const


# """
# PASSIVE_SEEKER_NOT_START(61001, "没有操作权限，请先开启挖掘被动求职者！"),
# PASSIVE_SEEKER_SORT_USER_NOT_EXIST(61002, "未能找到用户的推荐信息，无法获取排名！"),
# PASSIVE_SEEKER_SORT_COMPANY_NOT_EXIST(61003, "无法获取公司信息，无法获取排名！"),
# PASSIVE_SEEKER_SORT_COLLEAGUE_NOT_EXIST(61004, "无法获取公司其他成员信息，无法获取排名！"),
# PASSIVE_SEEKER_RECOMMEND_PARAM_ILLEGAL(61005, "是否推荐参数不合法！"),
# PASSIVE_SEEKER_CANDIDATES_POSITION_NOT_EXIST(61006, "没有合适的职位信息！"),
# PASSIVE_SEEKER_CANDIDATES_RECORD_NOT_EXIST(61007, "没有推荐记录！"),
# PASSIVE_SEEKER_APPLY_POSITION_ALREADY_APPLY(61008, "重复申请职位！"),
# PASSIVE_SEEKER_ALREADY_APPLIED_OR_RECOMMEND(61009, "已经申请或者被推荐");
# """


class RecomCustomVariableMixIn(BaseHandler):

    @tornado.gen.coroutine
    def prepare(self):
        """构建一些推荐候选人需要的相关环境变量"""

        yield super().prepare()
        yield self.refresh_recom_info()

    @tornado.gen.coroutine
    def refresh_recom_info(self):
        """构建一些推荐候选人需要的相关环境变量
        在 prepare 以及推荐后调用，保持推荐数据为最新状态
        """

        # 当前公司推荐积分配置
        reward_config = yield self.company_ps.get_company_reward_by_templateid(
            company_id=self.current_user.company.id,
            tempalte_id=const.RECRUIT_STATUS_FULL_RECOM_INFO_ID)

        # 当前员工总积分
        employee_reward = yield self.user_ps.get_employee_total_points(
            self.current_user.employee.id)

        # 当前员工获取的推荐积分总数
        hb_total = yield self.user_ps.get_employee_recommend_hb_amount(
            self.current_user.company.id,
            self.current_user.qxuser.id)

        self.employee_reward = str(employee_reward)
        self.reward_config = str(reward_config)
        self.hb_total = str(hb_total)

        # 推荐结果 message 模版，先获取自定义，在获取 default
        self._recommend_success_template = \
            self.current_user.company.conf_recommend_success or msg.DEFAULT_RECOMMEND_SUCCESS
        self._recommend_presentee_template = \
            self.current_user.company.conf.recommend_presentee or msg.DEFAULT_RECOMMEND_PRESENTEE

        self.recommend_success = self._recommend_success_template \
            .replace("{current_reward}",
                     '<span class="passive-reward">' + self.employee_reward + '</span>') \
            .replace("{recom_reward}",
                     '<span class="passive-reward">' + self.reward_config + '</span>') \
            .replace("{recom_hb}",
                     '<span class="passive-reward">' + self.hb_total + '</span>')

        self.recommend_presentee = self._recommend_presentee_template \
            .replace("{current_reward}",
                     '<span class="passive-reward">' + self.employee_reward + '</span>') \
            .replace("{recom_reward}",
                     '<span class="passive-reward">' + self.reward_config + '</span>') \
            .replace("{recom_hb}",
                     '<span class="passive-reward">' + self.hb_total + '</span>')


class RecomIgnoreHandler(RecomCustomVariableMixIn, BaseHandler):
    """跳过推荐该被动求职者
    """

    @tornado.gen.coroutine
    def post(self):
        """uri: /passiveseeker/ignore

        parameter
        id:推荐表编号
        is_recom:推荐状态 0：已推荐 1：未推荐 2：暂时忽略
        company_id:部门编号

        检查是否开启被动求职者。将推荐列表中对应用户置为已经推荐。
        如果还有下一个被动求职者，信息保存后，带上下一个推荐成员的信息，如果没有下一个，跳到推荐成功页面。

        response:
        json:
        {
           "id": "recom_record.id",
           "position_name":  //职位名称,
           "presentee_name": //nickname,
           "next":0,         //next:0 有下一个， 1:无,
           "errcode":0,      //errcode
           "errmsg":"",      //errcode
        }
        """

        if not self.current_user.employee:
            self.write_error(416, message=msg.EMPLOYEE_NOT_BINDED_WARNING)
            return

        recom_record_id = self.params.get("_id")
        click_time = self.get_argument("click_time")
        is_recom = 2 # 暂时忽略

        # TODO 调用基础服务
        #
        # passive_seeker = self.recomService.ignore_passive_seeker(
        #     self.post_user_id, click_time, recom_record_id,
        #     self.current_user.company.id,
        #     is_recom)
        passive_seeker = {}


        # recom_total 推荐总数， recom_index ： 已推荐人数
        if passive_seeker.get('recom_total') == (passive_seeker.get('recom_index') + passive_seeker.get('recom_ignore')):
            # TODO 调用基础服务
            stats = self.recomService.get_recom_stats(self.current_user.company.id, self.post_user_id)

            self.LOG.debug("post_ignore_passive_seeker stats: %s" % stats)

            # {"errcode":2102, "errmsg":"未能找到用户的推荐信息，无法获取排名！"}
            if stats.get('errcode') == 2102:
                self.render("refer/weixin/passive-seeker/passive-wanting_no-more.html")
                return

            stats['hongbao'] = int(passive_seeker.get('recom_index')) * 2 if stats else 0
            self.render("refer/weixin/passive-seeker/passive-wanting_finished.html",
                        stats=stats,
                        recommend_success=self.recommend_success)
            return

        self.render("refer/weixin/passive-seeker/passive-wanting_form.html",
                    passive_seeker=passive_seeker,
                    recommend_presentee=self.recommend_presentee)


class RecomCandidateHandler(RecomCustomVariableMixIn, BaseHandler):

    @tornado.gen.coroutine
    def get(self):
        if not self.current_user.employee:
            self.write_error(416, message=msg.EMPLOYEE_NOT_BINDED_WARNING)
            return

        id = self.params.id

        if id:
            yield self._get_recom_candidate(id)
        else:
            yield self._get_recom_candidates()

    @tornado.gen.coroutine
    def post(self):
        if not self.current_user.employee:
            self.write_error(416, message=msg.EMPLOYEE_NOT_BINDED_WARNING)
            return

        id = self.params.get('_id')

        if id:
            yield self._post_recom_candidate(id)
        else:
            yield self._post_recom_candidates()

    @tornado.gen.coroutine
    def _get_recom_candidate(self, id):
        # TODO
        # 调用基础服务
        # passive_seeker = self.recomService.get_recom_record_by_id(
        #     self.post_user_id, id)
        passive_seeker = {}

        if passive_seeker:
            passive_seeker.update(recom_index=0, recom_total=1, recom_ignore=0)
            self.render("refer/weixin/passive-seeker/passive-wanting_form.html",
                        passive_seeker=passive_seeker,
                        recommend_presentee=self.recommend_presentee)
        else:
            self.render("refer/weixin/passive-seeker/passive-wanting_no-more.html")

    @tornado.gen.coroutine
    def _get_recom_candidates(self):
        company_id = self.current_user.company.id
        click_time = self.get_argument("click_time", curr_now_dateonly())
        is_recom = ",".join(['1', '2', '3'])

        # TODO 调用基础服务
        # passive_seekers = self.recomService.get_passive_seekers(
        #     self.post_user_id, click_time, is_recom, company_id)

        passive_seekers = []
        if isinstance(passive_seekers, dict):
            # {'errcode': 2107, 'errmsg': '没有推荐记录！'}
            # {'errcode': 2101, "errmsg":"没有操作权限，请先开启被动求职者！"}
            if passive_seekers.get('errorcode') in [2107, 2101]:
                self.render(
                    "refer/weixin/passive-seeker/passive-wanting_no-more.html",
                    passive_seekers=passive_seekers,
                    message=passive_seekers.get('message'))

        elif isinstance(passive_seekers, list):
            for passive_seeker in passive_seekers:
                p_id = passive_seeker.get("position_id")
                for candidate in passive_seeker.get("candidates"):
                    user_id = candidate.get("presentee_user_id")
                    view_fav_res = self.recomService.get_wxuser_view_and_fav(
                        self.db, p_id, user_id)
                    candidate["view_number"] = view_fav_res.get("view_number",
                                                                0)
                    candidate["is_interested"] = view_fav_res.get(
                        "is_interested", 0)
            self.LOG.debug("get_passive_seekers: %s" % passive_seekers)

        self.render("refer/weixin/passive-seeker/passive-wanting_recom.html",
                    passive_seekers=passive_seekers,
                    message="placeholder")

    @tornado.gen.coroutine
    def _post_recom_candidate(self, id):
        from util.tool.str_tool import mobile_validate

        recom_record_id = id
        click_time = self.get_argument("click_time")
        realname = self.get_argument("_realname")
        company = self.get_argument("_company")
        position = self.get_argument("_position")
        mobile = self.get_argument("_mobile")
        recom_reason = self.get_argument("_recom_reason")

        form_items = [recom_record_id,
                      self.current_user.sysuser.id,
                      click_time,
                      realname,
                      company,
                      position,
                      recom_reason]

        self.LOG.debug("post_recom_passive_seeker form_items: %s" % form_items)

        # 如果校验失败返回原页面并附加 message
        message = None
        if any([(x == '') for x in form_items]):
            message = '有必填项未填写'
        elif mobile and not mobile_validate(mobile):
            message = '手机号格式校验失败'

        if message:
            passive_seeker = {
                'id':             recom_record_id,
                'realname':       realname,
                'company':        company,
                'position':       position,
                'mobile':         mobile,
                'recom_reason':   recom_reason,
                'recom_index':    self.get_argument("_recom_index"),
                'presentee_name': self.get_argument("_presentee_name"),
                'position_name':  self.get_argument("_position_name"),
                'message':        message
            }
            self.render(
                'refer/weixin/passive-seeker/passive-wanting_form.html',
                passive_seeker=passive_seeker,
                recommend_presentee=self.recommend_presentee)
            return

        # {u'presentee_name': u'\u8e0f\u96ea\u65e0\u75d5', u'errcode': 0, u'next': u'0', u'position_name': u'CK\u6d4b\u8bd5\u804c\u4f4d\u540d\u79f0', u'id': u'69', u'errmsg': u'\u5019\u9009\u4eba\u9009\u4e2d\u6210\u529f!'}

        # TODO 调用基础服务
        # passive_seeker = self.recomService.recom_passive_seeker(
        #     self.post_user_id, click_time, recom_record_id, realname, company,
        #     position, mobile, recom_reason,
        #     self.current_user.company.id)
        passive_seeker = {}

        self.LOG.debug("post_recom_passive_seeker passive_seeker: %s" % passive_seeker)

        # 推荐完成以后需要重新获取一下总积分
        yield self.refresh_recom_info()

        position_title = yield self.redpacket_ps.get_position_title_by_recom_record_id(recom_record_id)
        yield self.redpacket_ps.handle_red_packet_recom(
            recom_current_user=self.current_user,
            recom_record_id=recom_record_id,
            redislocker=self.redis,
            realname=realname,
            position_title=position_title
        )

        # # ===== 红包第二版 (RED PACKET V2 ) 开始 =====
        # # 推荐评价红包
        # company_id = self.current_user.company.id
        #
        # hb_config = get_hongbao_config_by_company_id(
        #     self.db, company_id, rptype=const.RED_PACKET_TYPE_RECOM)
        #
        # rp_ser = red_packet_service.RedPacketService()
        #
        # position_title = get_position_title_by_recom_record_id(
        #     self.db, recom_record_id).title
        #
        # is_service_wechat = self.current_user.wechat.type == 1
        # if is_service_wechat:
        #     recom_openid = self.current_user.wxuser.openid
        #     recom_wechat_id = self.current_user.wechat.id
        #     recom_qx_user = None
        # else:
        #     recom_openid = self.current_user.qxuser.openid
        #     recom_wechat_id = settings.bagging_wechat_id
        #     recom_qx_user = self.current_user.qxuser
        #
        # if hb_config:
        #     self.LOG.debug(u"推荐评价红包发送开始")
        #     if rp_ser.hit_red_packet(hb_config.probability):
        #         self.LOG.debug(u"用户是发送红包对象,准备掷骰子")
        #         if rp_ser.check_throttle_passed(self,
        #                                         hb_config,
        #                                         self.current_user.qxuser.id,
        #                                         position=None):
        #             self.LOG.debug(u"全局上限验证通过")
        #             # 发送红包消息模版(有金额)
        #             rp_ser.send_red_packet_card(
        #                 self,
        #                 recom_openid,
        #                 recom_wechat_id,
        #                 hb_config,
        #                 self.current_user.qxuser.id,
        #                 position=None,
        #                 company_name=self.current_user.company.name,
        #                 recomee_name=realname,
        #                 position_title=position_title,
        #                 recom_qx_user=recom_qx_user
        #             )
        #         else:
        #             self.LOG.debug(u"全局上限验证不通过, 暂停发送")
        #
        #     else:
        #         # 发送红包消息模版(抽不中)
        #         self.LOG.debug(u"掷骰子不通过,准备发送红包信封(无金额)")
        #         rp_ser.send_zero_amount_card(
        #             self,
        #             recom_openid,
        #             recom_wechat_id,
        #             hb_config,
        #             self.current_user.qxuser.id,
        #             company_name=self.current_user.company.name,
        #             recomee_name=realname,
        #             position_title=position_title,
        #             recom_qx_user=recom_qx_user
        #         )
        #
        # self.LOG.debug(u"推荐评价红包发送结束")
        # # ===== 红包第二版 (RED PACKET V2 ) 结束 =====


        # 已经全部推荐了
        if passive_seeker.get('recom_total') == passive_seeker.get(
            'recom_index') + passive_seeker.get('recom_ignore'):
            stats = self.recomService.get_recom_stats(
                self.current_user.company.id, self.post_user_id)
            stats['hongbao'] = int(
                passive_seeker.get('recom_index')) * 2 if stats else 0
            self.LOG.debug("post_recom_passive_seeker stats: %s" % stats)
            self.render(
                "refer/weixin/passive-seeker/passive-wanting_finished.html",
                stats=stats, recommend_success=self.recommend_success)

        else:  # 还有未推荐的
            self.render(
                "refer/weixin/passive-seeker/passive-wanting_form.html",
                passive_seeker=passive_seeker,
                recommend_presentee=self.recommend_presentee)

    @tornado.gen.coroutine
    def _post_recom_candidates(self):
        ids = self.get_arguments("_ids")

        if not ids:
            self.get_passive_seekers('请选择推荐人！')
            return

        self.LOG.debug(",".join(ids))

        # 更新被动求职者的推荐状态为选中 is_recom:2
        # TODO 调用基础服务
        passive_seeker = self.recomService.recom_passive_seekers(
            self.current_user.company.id, ",".join(ids))

        # {u'presentee_name': u'\u8e0f\u96ea\u65e0\u75d5', u'errcode': 0, u'next': u'0', u'position_name': u'CK\u6d4b\u8bd5\u804c\u4f4d\u540d\u79f0', u'id': u'69', u'errmsg': u'\u5019\u9009\u4eba\u9009\u4e2d\u6210\u529f!'}
        self.LOG.debug("post_passive_seekers: %s" % passive_seeker)

        # 返回第一个推荐的被动求职者
        self.render("refer/weixin/passive-seeker/passive-wanting_form.html",
                    passive_seeker=passive_seeker,
                    recommend_presentee=self.recommend_presentee)

