# coding=utf-8

from tornado import gen

from handler.base import BaseHandler

import conf.common as const
import conf.path as path
import conf.message as msg

from util.common import ObjectDict
from util.common.decorator import check_signature
from util.tool.url_tool import make_url
from util.tool.str_tool import gen_salary

class PositionHandler(BaseHandler):

    @check_signature
    @gen.coroutine
    def get(self, position_id):
        """显示 JD 页
        """
        position_info = yield self.position_ps.get_position(position_id)

        if position_info.id:

            # 是否收藏
            star = yield self.position_ps.is_position_stared_by(
                position_id, self.current_user.sysuser.id)

            # 是否申请
            application = yield self.application_ps.get_application(
                position_id, self.current_user.sysuser.id)

            # 获得职位所属公司信息
            real_company_id = yield self.position_ps.get_real_company_id(position_info.publisher, position_info.company_id)
            company_info = yield self.company_ps.get_company(conds={"id": real_company_id}, need_conf=True)

            # 构建转发信息
            self._make_share_info(position_info, company_info)

            # HR头像及底部转发文案
            endorse = self._make_endorse_info(position_info, company_info)

            # 是否超出投递上限。每月每家公司一个人只能申请3次
            can_apply = yield self.application_ps.is_allowed_apply_position(
                self.current_user.sysuser.id, company_info.id)

            # 诺华定制。本次不实现

            # 相似职位推荐
            recomment_positions_res = yield self.position_ps.get_recommend_positions(position_id)

            position_data = ObjectDict({
                "header": self._make_json_header(position_info, company_info, star, application, endorse, can_apply),
                "module_job_description": self._make_json_job_description(position_info),
                "module_job_require": self._make_json_job_require(position_info),
                "module_job_need": self._make_json_job_need(position_info),
                "module_feature": self._make_json_job_feature(position_info),
                "module_company_info": self._make_json_job_company_info(company_info),
                "module_position_recommend": self._make_recommend_positions(recomment_positions_res),
            })
            data = ObjectDict({
                "position": position_data
            })

            self.render_page("", data=data)

            # 后置操作
            # 刷新链路


        else:
            self.write_error(404)
            return


            # 记录推荐者推荐职位的查看记录
            if self.current_user.recom:
                share_params = mdict()
                share_params.wechat_id = self.current_user.wechat.id
                share_params.recom_id = self.current_user.recom.get("id", 0)
                share_params.position_id = position.id
                share_params.presentee_id = self.current_user.wxuser.get("id",
                                                                         0)
                share_params.sysuser_id = self.current_user.sysuser.get("id",
                                                                        0)
                share_params.viewer_id = self.current_user.viewer.idcode
                share_params.viewer_ip = self.request.remote_ip
                share_params.source = const.ONUSE if self.PROJECT == \
                                                     const.PROJECT_PLATFORM \
                    else const.UNUSED
                # '来自, 0:未知, 朋友圈(timeline ) 1, 微信群(groupmessage) 2,
                # 个人消息(singlemessage) 3'
                click_from = {'timeline':      1, 'groupmessage': 2,
                              'singlemessage': 3}
                share_params.click_from = const.DICT_CLICK_FROM.get(
                    self.get_argument("from", "unknow"), 0)
                self.sysuserService.insert_sysuser_position_share_record(
                    share_params)

                # 需要实时算出链路数据
                if position.status == 0:
                    res = refresh_share_chain(self,
                                              wxuser_id=self.current_user.wxuser.id,
                                              position_id=position.id)
                    self.LOG.debug("refresh_share_chain : {0}".format(res))

            # 记录候选人
            # 需要在刷新完候选人链路信息后调用
            send_candidate_params = {
                "wxuser_id":     self.current_user.wxuser.id,
                "position_id":   self.params.pid,
                "from_employee": 0
            }
            if self.current_user.recom:
                last_employee_recom_id = get_referral_employee_wxuser_id(
                    self, self.current_user.wxuser.id, position.id)
                send_candidate_params.update({
                    "from_employee": 1 if last_employee_recom_id else 0
                })

            send_candidate = wxuserService(
                self.db).send_candidate_view_position
            tornado.ioloop.IOLoop.instance().add_callback(send_candidate,
                                                          send_candidate_params)

            last_recom_wxuser_id = get_referral_employee_wxuser_id(self,
                                                                   self.current_user.wxuser.id,
                                                                   self.params.pid)
            # 转发被点击加积分
            self.LOG.debug("get_reward_be_click{0},{1}".format(
                self.current_user.wxuser.id, last_recom_wxuser_id))

            # 注意!
            # self.current_user.employee 仅代表 current_user 是否是某个公司的员工
            # 这并不意味着 current_user.employee 存在就代表这个 user 是当前公众号的员工
            # 要判断当前用户是否是当前公众号的员工,
            # 需要判断 1. employee 是否存在
            #         2.验证 employee.company_id 和 当前公众号的 company_id

            if ((not self.current_user.employee.exist or
                         self.current_user.employee.company_id !=
                         self.current_user.wechat.company_id) and
                    last_recom_wxuser_id and self.current_user.wxuser.id and
                        self.current_user.wxuser.id != last_recom_wxuser_id):
                self.LOG.debug("Begin_add_reward_be_click")
                employeeService(self.db).add_reward_for_recom_click(
                    wxuser_id=self.current_user.wxuser.id,
                    last_recom_wxuser_id=last_recom_wxuser_id,
                    position_id=self.params.pid,
                    company_id=self.current_user.company.id)

            if self.PROJECT == const.PROJECT_PLATFORM:
                yield rp_ser.handle_red_packet_position_related(self, position,
                                                                is_click=True)

            # 如果该职位浏览量达到5次,给发布者发送模板消息
            if position.get("visitnum", 0) == 4 and position.get("source",
                                                                 -1) == 0:
                self.send_publish_template(position)


    def _make_recom(self):
        """用于微信分享和职位推荐时，传出的 recom 参数"""

        return self.current_user.wxuser.openid

    def _make_share_info(self, position_info, company_info):
        """构建 share 内容"""

        # 如果有红包，则取红包的分享文案
        red_packet = yield self.redpacket_ps.get_last_running_hongbao_config_by_position(position_info)

        if red_packet:
            cover = self.static_url(red_packet.share_img)
            title = "{} {}".format(position_info.title, red_packet.share_title)
            description = red_packet.share_desc
        else:
            cover = self.static_url(company_info.logo)
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

        self.params.share = ObjectDict({
            "cover": cover,
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

        endorse = ObjectDict({
            "publisher": position_info.publisher,
            "is_hr": is_hr,
            "avatar": self.static_url(hrheadimgurl),
            "name": hr_name,
            "company": company_name,
            "department": position_info.department
        })

        raise gen.Return(endorse)

    @gen.coroutine
    def _make_recommend_positions(self, positions):
        """处理相似职位推荐"""

        data = []
        for item in positions:
            pos = ObjectDict()
            pos.title = item.get("job_title")
            pos.location = item.get("job_city", "")
            pos.salary = gen_salary(item.get("salary_top"), item.get("salary_bottom"))
            pos.link = make_url(path.POSITION_PATH.format(item.get("pid")), self.params,
                                escape=["keywords, cities, candidate_source, employment_type, salary, "
                                        "department, occupations, custom, degree, page_from, page_size"])
            data.append(pos)
            if len(data) > 2:
                break

        res = ObjectDict({
            "title": "相关职位推荐",
            "data": data
        })

        raise gen.Return(res)

    @gen.coroutine
    def _make_json_header(self, position_info, company_info, star, application, endorse, can_apply):
        """构造头部 header 信息"""
        data = ObjectDict({
            "id": position_info.id,
            "title": position_info.title,
            "disable": True if position_info.status == 0 else False,
            "location": position_info.city,
            "update_time": position_info.update_time,
            "star": star,
            "icon_url": self.static_url(company_info.logo),
            "submitted": bool(application),
            "appid": application.id,
            "endorse": endorse,
            "can_apply": can_apply,
            "forword_message": company_info.conf_forward_message or const.POSITION_FORWARD_MESSAGE
        })

        raise gen.Return(data)

    @gen.coroutine
    def _make_json_job_description(self, position_info):
        """构造职位描述"""
        data = ObjectDict({
            "data": position_info.accountabilities,
        })

        raise gen.Return(data)

    @gen.coroutine
    def _make_json_job_require(self, position_info):
        """构造职位要求"""
        require = []
        if position_info.degree:
            require.append("学历 {}".format(position_info.degree))
        if position_info.experience:
            require.append("工作经验 {}".format(position_info.experience))
        if position_info.language:
            require.append("语言要求 {}".format(position_info.language))
        data = ObjectDict({
            "data":  require
        })

        raise gen.Return(data)

    @gen.coroutine
    def _make_json_job_need(self, position_info):
        """构造职位要求"""
        data = ObjectDict({
            "data": position_info.requirement,
        })

        raise gen.Return(data)

    @gen.coroutine
    def _make_json_job_feature(self, position_info):
        """构造职位福利特色"""
        data = ObjectDict({
            "data": position_info.feature,
        })

        raise gen.Return(data)

    @gen.coroutine
    def _make_json_job_company_info(self, company_info):
        """构造职位公司信息"""
        data = ObjectDict({
            "icon_url": company_info.logo,
            "name": company_info.name or company_info.abbreviation,
            "descripthon": company_info.introduction,
        })

        raise gen.Return(data)

    @gen.coroutine
    def _make_refresh_share_chain(self, position_info):
        """构造刷新链路"""

        if self.current_user.recom.id:
            params = ObjectDict()
            params.wechat_id = self.current_user.wechat.id
            params.recom_id = self.current_user.recom.id
            params.position_id = position_info.id
            params.presentee_id = self.current_user.wxuser.id
            params.sysuser_id = self.current_user.sysuser.id
            params.viewer_id = 0
            params.viewer_ip = self.request.remote_ip
            params.source = const.ONUSE if self.PROJECT == const.PROJECT_PLATFORM \
                else const.UNUSED
            # '来自, 0:未知, 朋友圈(timeline ) 1, 微信群(groupmessage) 2,
            # 个人消息(singlemessage) 3'
            click_from = {'timeline': 1, 'groupmessage': 2,
                          'singlemessage': 3}
            share_params.click_from = const.DICT_CLICK_FROM.get(
                self.get_argument("from", "unknow"), 0)
            self.sysuserService.insert_sysuser_position_share_record(
                share_params)

            # 需要实时算出链路数据
            if position.status == 0:
                res = refresh_share_chain(self,
                                          wxuser_id=self.current_user.wxuser.id,
                                          position_id=position.id)
                self.LOG.debug("refresh_share_chain : {0}".format(res))

