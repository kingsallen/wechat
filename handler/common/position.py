# coding=utf-8

from tornado import gen

from handler.base import BaseHandler
from util.common.decorator import check_signature
from util.tool.url_tool import make_url
import conf.common as const
import conf.path as path
import conf.message as msg
from util.common import ObjectDict


class PositionHandler(BaseHandler):

    @check_signature
    @gen.coroutine
    def get(self, position_id):
        """显示 JD 页
        1.判断是否收藏
        2.判断是否申请
        3.构建自定义转发链路


        """
        position_info = yield self.position_ps.get_position(position_id)

        if position_info.id:

            # 是否收藏
            star = yield self.position_ps.is_position_stared_by(
                position_id, self.current_user.sysuser.id)
            self.params._star = star

            # 是否申请
            application = yield self.application_ps.get_application(
                position_id, self.current_user.sysuser.id)
            self.params._submitted = bool(application)
            self.params.app_id = application.id

            # 获得职位所属公司信息
            company_info = yield self.position_ps.get_company_info(position_info.publisher, position_info.company_id)

            # 构建转发信息
            self._make_share_info(position_info, company_info)

            # HR头像及底部转发文案
            self._make_endorse_info(position_info, company_info)

            # 是否超出投递上限。每月每家公司一个人只能申请3次
            is_allowed_apply_count = yield self.application_ps.is_allowed_apply_position(
                self.current_user.sysuser.id, company_info.id)
            self.params._can_apply = is_allowed_apply_count



        else:
            self.write_error(404)
            return

            # TODO panda JD 页 实现
            # # IM聊天未读消息
            # unread_num = 1
            # if self.current_user.wxuser.sysuser_id and position.publisher:
            #     wx_hr_chat_room_info = {
            #         "sysuser_id": self.current_user.wxuser.sysuser_id,
            #         "account_id": position.publisher}
            #     wx_hr_chat_room = yield WxHrChatListService().get_chat_room(
            #         wx_hr_chat_room_info)
            #     if wx_hr_chat_room and wx_hr_chat_room.get("id"):
            #         unread_recodes = {
            #             "chatlist_id": wx_hr_chat_room.get("id"),
            #             "speaker":     0
            #         }
            #         unread_num = yield WxHrChatService(
            #
            #         ).get_unread_recodes_num(
            #             unread_recodes)
            #         unread_num = int(unread_num)
            #
            #
            # # 获取推荐朋友浮层文案
            # res = pos_ser.get_forward_custom_message(
            #     self.current_user.company.id)
            # forward_message = res.get("forward_message",
            #                           "") or msg.DEFAULT_FORWARD_MESSAGE
            #
            # # 定制插入
            # custom_service = CustomService(self.db)
            # # 1. 诺华定制
            # suppress_apply = custom_service.get_suppress_apply(position)
            # self.LOG.debug("suppress_apply:{}".format(suppress_apply))
            # # 2. 开启代理投递
            # delegate_drop = custom_service.get_delegate_drop(self)
            #
            # # 计算相关职位, 调用基础服务接口
            # related_positions = yield pos_ser.get_position_recommend(
            #     param={"pid": position.get("id")}
            # )
            #
            # related_positions = []
            #
            # self.render("neo_weixin/position/position_info.html",
            #             position=position,
            #             related_positions=related_positions,
            #             endorse_info=endorse_info,
            #             unread_num=unread_num,
            #             impression=position.impression,
            #             forward_message=forward_message,
            #             suppress_apply=suppress_apply,
            #             delegate_drop=delegate_drop  # 采用代理投递整体配置, 建议JD页分块传递参数
            #             )
            #
            # # 记录推荐者推荐职位的查看记录
            # if self.current_user.recom:
            #     share_params = mdict()
            #     share_params.wechat_id = self.current_user.wechat.id
            #     share_params.recom_id = self.current_user.recom.get("id", 0)
            #     share_params.position_id = position.id
            #     share_params.presentee_id = self.current_user.wxuser.get("id",
            #                                                              0)
            #     share_params.sysuser_id = self.current_user.sysuser.get("id",
            #                                                             0)
            #     share_params.viewer_id = self.current_user.viewer.idcode
            #     share_params.viewer_ip = self.request.remote_ip
            #     share_params.source = const.ONUSE if self.PROJECT == \
            #                                          const.PROJECT_PLATFORM \
            #         else const.UNUSED
            #     # '来自, 0:未知, 朋友圈(timeline ) 1, 微信群(groupmessage) 2,
            #     # 个人消息(singlemessage) 3'
            #     click_from = {'timeline':      1, 'groupmessage': 2,
            #                   'singlemessage': 3}
            #     share_params.click_from = const.DICT_CLICK_FROM.get(
            #         self.get_argument("from", "unknow"), 0)
            #     self.sysuserService.insert_sysuser_position_share_record(
            #         share_params)
            #
            #     # 需要实时算出链路数据
            #     if position.status == 0:
            #         res = refresh_share_chain(self,
            #                                   wxuser_id=self.current_user.wxuser.id,
            #                                   position_id=position.id)
            #         self.LOG.debug("refresh_share_chain : {0}".format(res))
            #
            # # 记录候选人
            # # 需要在刷新完候选人链路信息后调用
            # send_candidate_params = {
            #     "wxuser_id":     self.current_user.wxuser.id,
            #     "position_id":   self.params.pid,
            #     "from_employee": 0
            # }
            # if self.current_user.recom:
            #     last_employee_recom_id = get_referral_employee_wxuser_id(
            #         self, self.current_user.wxuser.id, position.id)
            #     send_candidate_params.update({
            #         "from_employee": 1 if last_employee_recom_id else 0
            #     })
            #
            # send_candidate = wxuserService(
            #     self.db).send_candidate_view_position
            # tornado.ioloop.IOLoop.instance().add_callback(send_candidate,
            #                                               send_candidate_params)
            #
            # last_recom_wxuser_id = get_referral_employee_wxuser_id(self,
            #                                                        self.current_user.wxuser.id,
            #                                                        self.params.pid)
            # # 转发被点击加积分
            # self.LOG.debug("get_reward_be_click{0},{1}".format(
            #     self.current_user.wxuser.id, last_recom_wxuser_id))
            #
            # # 注意!
            # # self.current_user.employee 仅代表 current_user 是否是某个公司的员工
            # # 这并不意味着 current_user.employee 存在就代表这个 user 是当前公众号的员工
            # # 要判断当前用户是否是当前公众号的员工,
            # # 需要判断 1. employee 是否存在
            # #         2.验证 employee.company_id 和 当前公众号的 company_id
            #
            # if ((not self.current_user.employee.exist or
            #              self.current_user.employee.company_id !=
            #              self.current_user.wechat.company_id) and
            #         last_recom_wxuser_id and self.current_user.wxuser.id and
            #             self.current_user.wxuser.id != last_recom_wxuser_id):
            #     self.LOG.debug("Begin_add_reward_be_click")
            #     employeeService(self.db).add_reward_for_recom_click(
            #         wxuser_id=self.current_user.wxuser.id,
            #         last_recom_wxuser_id=last_recom_wxuser_id,
            #         position_id=self.params.pid,
            #         company_id=self.current_user.company.id)
            #
            # if self.PROJECT == const.PROJECT_PLATFORM:
            #     yield rp_ser.handle_red_packet_position_related(self, position,
            #                                                     is_click=True)
            #
            # # 如果该职位浏览量达到5次,给发布者发送模板消息
            # if position.get("visitnum", 0) == 4 and position.get("source",
            #                                                      -1) == 0:
            #     self.send_publish_template(position)


    def _make_recom(self):
        """用于微信分享和职位推荐时，传出的 recom 参数"""

        return self.current_user.wxuser.openid

    def _make_share_info(self, position_info, company_info):
        """构建 share 内容"""

        # 如果有红包，则取红包的分享文案
        # rp_ser = red_packet_service.RedPacketService()
        # rp_config = rp_ser.get_last_running_hongbao_config_by_position(
        #     position)
        # if rp_config:
        #     self.params.share = mdict({
        #         "cover": self.static_url(
        #             rp_config.share_img, include_host="http"),
        #         "title": position.title + " " + rp_config.share_title,
        #         "description": rp_config.share_desc,
        #         "link": url.make_url(
        #             const.POSITION_URL,
        #             self.params,
        #             host=self.request.host,
        #             protocol=self.request.protocol,
        #             m="info",
        #             recom=self.params._in_order_to_recom,
        #             escape=["wid", "tjtoken", "tj", "occupation", "hb_c"])
        #     })
        #
        # self.LOG.debug("share_test position_info 2: %s" % self.params)

        title = position_info.title
        description = msg.SHARE_DES_DEFAULT

        if position_info.share_title:
            title = str(position_info.share_title).format(
                company=company_info.abbreviation,
                position=position_info.title)

        if position_info.share_description:
            description = position_info.share_description

        link = make_url(path.POSITION_PATH.format(position_info.id), self.params,
                        recom=self._make_recom(),
                        escape=["keywords, cities, candidate_source, employment_type, salary, "
                                "department, occupations, custom, degree, page_from, page_size"])

        self.params._share = ObjectDict({
            "cover": self.static_url(company_info.logo),
            "title": title,
            "description": description,
            "link": link
        })


    @gen.coroutine
    def _make_hr_info(self, publisher):
        """根据职位 publisher 返回 hr 的相关信息 tuple"""
        hr_account, hr_wx_user = yield self.position_ps.get_hr_info(publisher)
        raise gen.Return((hr_account, hr_wx_user))


    @gen.coroutine
    def _make_endorse_info(self, position_info, company_info):
        """构建 JD 页左下角背书信息"""
        hr_account, hr_wx_user = yield self._make_hr_info(position_info.publisher)
        hrheadimgurl = (
            hr_account.headimgurl or hr_wx_user.headimgurl or
            company_info.logo or const.HR_HEADIMG
        )

        hr_name = hr_account.name or hr_wx_user.nickname or ''
        company_name = company_info.abbreviation or company_info.company_name or ''

        is_hr = self.current_user.qxuser.unionid == hr_wx_user.unionid

        self.params_endorse_info = ObjectDict({
            "is_hr": is_hr,
            "endorse_src": self.static_url(hrheadimgurl),
            "endorse_name": hr_name,
            "endorse_company": company_name,
            "endorse_department": position_info.department
        })
