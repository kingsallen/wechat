# coding=utf-8

import functools
from tornado import gen

from handler.base import BaseHandler

import conf.common as const
import conf.path as path
import conf.message as msg
import conf.wechat as wx

from util.common import ObjectDict
from util.common.decorator import handle_response
from util.tool.url_tool import make_url
from util.tool.str_tool import gen_salary, add_item, split
from util.wechat.template import position_view_five


class PositionHandler(BaseHandler):

    @gen.coroutine
    def get(self, position_id):
        """显示 JD 页
        """
        position_info = yield self.position_ps.get_position(position_id)

        if position_info.id:
            self.logger.debug("[JD]构建收藏信息")
            star = yield self.position_ps.is_position_stared_by(
                position_id, self.current_user.sysuser.id)

            self.logger.debug("[JD]构建申请信息")
            application = yield self.application_ps.get_application(
                position_id, self.current_user.sysuser.id)

            self.logger.debug("[JD]构建职位所属公司信息")
            real_company_id = yield self.company_ps.get_real_company_id(position_info.publisher, position_info.company_id)
            company_info = yield self.company_ps.get_company(conds={"id": real_company_id}, need_conf=True)

            self.logger.debug("[JD]构建转发信息")
            yield self._make_share_info(position_info, company_info)

            self.logger.debug("[JD]构建HR头像及底部转发文案")
            endorse = yield self._make_endorse_info(position_info, company_info)

            # 是否超出投递上限。每月每家公司一个人只能申请3次
            self.logger.debug("[JD]处理投递上限")
            can_apply = yield self.application_ps.is_allowed_apply_position(
                self.current_user.sysuser.id, company_info.id)

            # 诺华定制。本次不实现

            # 相似职位推荐
            self.logger.debug("[JD]构建相似职位推荐")
            recomment_positions_res = yield self.position_ps.get_recommend_positions(position_id)

            header = yield self._make_json_header(position_info, company_info, star, application, endorse, can_apply)
            module_job_description = yield self._make_json_job_description(position_info)
            module_job_require = yield self._make_json_job_require(position_info)
            module_job_need = yield self._make_json_job_need(position_info)
            module_feature = yield self._make_json_job_feature(position_info)
            module_company_info = yield self._make_json_job_company_info(company_info)
            module_position_recommend = yield self._make_recommend_positions(recomment_positions_res)
            module_mate_day = yield self._make_mate_day(position_info)
            module_team = yield self._make_team(position_info)
            module_team_position = yield self._make_team_position(position_info)

            position_data = ObjectDict()
            add_item(position_data, "header", header)
            add_item(position_data, "module_job_description", module_job_description)
            add_item(position_data, "module_job_require", module_job_require)
            add_item(position_data, "module_job_need", module_job_need)
            add_item(position_data, "module_feature", module_feature)
            add_item(position_data, "module_company_info", module_company_info)
            add_item(position_data, "module_position_recommend", module_position_recommend)
            add_item(position_data, "module_mate_day", module_mate_day)
            add_item(position_data, "module_team", module_team)
            add_item(position_data, "module_team_position", module_team_position)

            self.logger.debug("position_data: %s" % position_data)
            self.logger.debug("self.params: %s" % self.params)

            self.render_page("position/info.html", data=position_data)

            # 后置操作
            # 刷新链路
            self.logger.debug("[JD]刷新链路")
            last_recom_wxuser_id = yield self._make_refresh_share_chain(position_info)
            self.logger.debug("[JD]last_recom_wxuser_id: %s" % last_recom_wxuser_id)

            # 红包处理
            if self.is_platform and self.current_user.recom:
                self.logger.debug("[JD]红包处理")
                yield self.redpacket_ps.handle_red_packet_position_related(
                    self.current_user, position_info, is_click=True)

            self.logger.debug("[JD]更新职位浏览量")
            yield self._make_position_visitnum(position_info)

            self.logger.debug("[JD]转发积分操作")
            yield self._make_add_reward_click(position_info, last_recom_wxuser_id)

            yield self._make_send_publish_template(position_info)

        else:
            self.write_error(404)
            return

    @gen.coroutine
    def _make_position_visitnum(self, position_info):
        """更新职位浏览量"""
        yield self.position_ps.update_position(conds={
            "id": position_info.id
        }, fields={
            "visitnum": position_info.visitnum + 1,
            "update_time": position_info.update_time_ori,
        })

    def _make_recom(self):
        """用于微信分享和职位推荐时，传出的 recom 参数"""

        return self.current_user.wxuser.openid

    @gen.coroutine
    def _make_share_info(self, position_info, company_info):
        """构建 share 内容"""

        # 如果有红包，则取红包的分享文案
        red_packet = yield self.redpacket_ps.get_last_running_hongbao_config_by_position(position_info)

        self.logger.debug("自定义分享：%s" % red_packet)
        if red_packet:
            cover = self.static_url(red_packet.share_img)
            title = "{} {}".format(position_info.title, red_packet.share_title)
            description = "".join(split(red_packet.share_desc))
        else:
            cover = self.static_url(company_info.logo)
            title = position_info.title
            description = msg.SHARE_DES_DEFAULT

            if position_info.share_title:
                title = str(position_info.share_title).format(
                    company=company_info.abbreviation,
                    position=position_info.title)
            if position_info.share_description:
                description = "".join(split(position_info.share_description))

        link = make_url(path.POSITION_PATH.format(position_info.id),
            self.params,
            host=self.request.host,
            protocol=self.request.protocol,
            recom=self._make_recom(),
            escape=["pid", "keywords", "cities", "candidate_source",
                    "employment_type", "salary", "department", "occupations",
                    "custom", "degree", "page_from", "page_size"]
        )

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
                                escape=["pid", "keywords", "cities", "candidate_source", "employment_type", "salary",
                                "department", "occupations", "custom", "degree", "page_from", "page_size"])
            data.append(pos)
            if len(data) > 2:
                break

        if len(data) == 0:
            res = None
        else:
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
            "status": position_info.status,
            "location": position_info.city,
            "update_time": position_info.update_time,
            "star": star,
            "icon_url": self.static_url(company_info.logo),
            "submitted": bool(application),
            "appid": application.id,
            "endorse": endorse,
            "can_apply": not can_apply,
            "forword_message": company_info.conf_forward_message or msg.POSITION_FORWARD_MESSAGE,
            "team": position_info.department.lower() if position_info.department else ""
        })

        raise gen.Return(data)

    @gen.coroutine
    def _make_json_job_description(self, position_info):
        """构造职位描述"""
        if not position_info.accountabilities:
            data = None
        else:
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

        if len(require) == 0:
            data = None
        else:
            data = ObjectDict({
                "data":  require
            })

        raise gen.Return(data)

    @gen.coroutine
    def _make_json_job_need(self, position_info):
        """构造职位要求"""

        if not position_info.requirement:
            data = None
        else:
            data = ObjectDict({
                "data": position_info.requirement,
            })

        raise gen.Return(data)

    @gen.coroutine
    def _make_json_job_feature(self, position_info):
        """构造职位福利特色"""
        if not position_info.feature:
            data = None
        else:
            data = ObjectDict({
                "data": position_info.feature,
            })

        raise gen.Return(data)

    @gen.coroutine
    def _make_json_job_company_info(self, company_info):
        """构造职位公司信息"""
        data = ObjectDict({
            "icon_url": self.static_url(company_info.logo),
            "name": company_info.name or company_info.abbreviation,
            "description": company_info.introduction,
        })

        raise gen.Return(data)

    @gen.coroutine
    def _make_refresh_share_chain(self, position_info):
        """构造刷新链路"""

        last_recom_id = 0
        if self.current_user.recom:
            params = ObjectDict()
            params.wechat_id = self.current_user.wechat.id
            params.recom_id = self.current_user.recom.id
            params.position_id = position_info.id
            params.presentee_id = self.current_user.wxuser.id
            params.sysuser_id = self.current_user.sysuser.id
            params.viewer_id = 0
            params.viewer_ip = self.request.remote_ip
            params.source = 0 if self.is_platform else 1
            params.click_from = wx.CLICK_FROM.get(self.get_argument("from", ""), 0)
            yield self.sharechain_ps.create_share_record(params)

            # 需要实时算出链路数据
            if position_info.status == 0:
                res = yield self.sharechain_ps.refresh_share_chain(self.current_user.wxuser.id, position_info.id)
                if res:
                    last_recom_id = yield self.sharechain_ps.get_referral_employee_wxuser_id(self.current_user.wxuser.id, position_info.id)

        yield self.position_ps.send_candidate_view_position(params={
            "wxuser_id": self.current_user.wxuser.id,
            "position_id": position_info.id,
            "from_employee": 1 if last_recom_id else 0,
        })

        raise gen.Return(last_recom_id)

    @gen.coroutine
    def _make_add_reward_click(self, position_info, last_recom_wxuser_id):
        """给员工加积分"""

        if self.current_user.employee and last_recom_wxuser_id != self.current_user.wxuser.id:
            res = yield self.position_ps.add_reward_for_recom_click(self.current_user.employee,
                                                              self.current_user.company.id,
                                                              self.current_user.wxuser.id,
                                                              position_info.id,
                                                              last_recom_wxuser_id)
            self.logger.debug("给员工加积分： %s" % res)

    @gen.coroutine
    def _make_send_publish_template(self, position_info):
        """浏览量达到5次后，向 HR 发布模板消息
        注：只向 HR 平台发布的职位发送模板消息，ATS 同步的职位不发送"""

        if position_info.visitnum == 4 and position_info.source == 0:
            help_wechat = yield self.wechat_ps.get_wechat(conds={
                "signature": self.settings.helper_signature
            })

            hr_account, hr_wx_user = yield self._make_hr_info(position_info.publisher)

            if hr_wx_user.openid:
                # 如果企业有公众号，发企业链接，若无，发集合号链接
                if self.current_user.wechat:
                    link = make_url(path.POSITION_PATH.format(position_info.id), host=self.settings.platform_host,
                                    wechat_signature=self.current_user.wechat.signature)
                else:
                    link = make_url(path.OLD_POSITION_PATH, host=self.settings.qx_host, m="info", pid=position_info.id)

                yield position_view_five(help_wechat.id, hr_wx_user.openid, link, position_info.title,
                                   position_info.salary)

    @gen.coroutine
    def _make_team_position(self, position_info):
        """团队职位，构造数据"""

        # 构造假数据
        if not position_info.department:
            res = None
        else:
            department = position_info.department.lower()
            team = yield self.team_ps.get_more_team_info(department, params={
                "user_id": 0,
                "company_id": 0,
            })

            res = ObjectDict({
                "title": "我们团队还需要",
                "data": team.templates[2].data
            })

        raise gen.Return(res)

    @gen.coroutine
    def _make_mate_day(self, position_info):
        """同事的一天，构造数据"""

        # 构造假数据
        if not position_info.department:
            res = None
        else:
            department = position_info.department.lower()
            team = yield self.team_ps.get_more_team_info(department, params={
                "user_id": 0,
                "company_id": 0,
            })

            res = ObjectDict({
                "title": "同事的一天",
                "sub_type": "less",
                "data": [team.templates[1].data[0]]
            })

        raise gen.Return(res)

    @gen.coroutine
    def _make_team(self, position_info):
        """所属团队，构造数据"""

        # 构造假数据
        if not position_info.department:
            res = None
        else:
            department = position_info.department.lower()
            team = yield self.team_ps.get_more_team_info(department, params={
                "user_id": 0,
                "company_id": 0,
            })

            res = ObjectDict({
                "title": "所属团队",
                "sub_type": " full",
                "data": team.templates[0].data,
            })

        raise gen.Return(res)


class PositionStarHandler(BaseHandler):
    """处理收藏（加星）操作"""

    @handle_response
    @gen.coroutine
    def post(self):
        self.guarantee('star', 'pid')

        # 收藏操作
        if self.params.star:
            ret = yield self.user_ps.favorite_position(
                self.current_user, self.params.pid)
        else:
            ret = yield self.user_ps.unfavorite_position(
                self.current_user, self.params.pid)

        if ret:
            self.send_json_success()
        else:
            self.send_json_error()
