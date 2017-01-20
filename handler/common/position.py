# coding=utf-8

from tornado import gen

import conf.common as const
import conf.message as msg
import conf.path as path
import conf.wechat as wx
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response
from util.common.cipher import encode_id
from util.tool.str_tool import gen_salary, add_item, split
from util.tool.url_tool import make_url, url_append_query
from util.wechat.template import position_view_five
from tests.dev_data.user_company_config import COMPANY_CONFIG


class PositionHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self, position_id):
        """显示 JD 页
        """
        position_info = yield self.position_ps.get_position(position_id)

        if position_info.id and \
                position_info.company_id == self.current_user.company.id:
            yield self._redirect_when_recom_is_openid(position_info)
            if self.request.connection.stream.closed():
                return

            # hr端功能不全，暂且通过团队名称匹配
            team = yield self.team_ps.get_team_by_name(
                position_info.department, position_info.company_id)
            # team = yield self.team_ps.get_team_by_id(position_info.team_id)

            self.logger.debug("[JD]构建收藏信息")
            star = yield self.position_ps.is_position_stared_by(
                position_id, self.current_user.sysuser.id)

            self.logger.debug("[JD]构建申请信息")
            application = yield self.application_ps.get_application(
                position_id, self.current_user.sysuser.id)

            self.logger.debug("[JD]构建职位所属公司信息")
            real_company_id = yield self.company_ps.get_real_company_id(
                position_info.publisher, position_info.company_id)
            company_info = yield self.company_ps.get_company(
                conds={"id": real_company_id}, need_conf=True)

            did = real_company_id if \
                real_company_id != self.current_user.company.id else ''

            # 刷新链路
            self.logger.debug("[JD]刷新链路")
            last_employee_user_id = yield self._make_refresh_share_chain(
                position_info)
            self.logger.debug(
                "[JD]last_employee_user_id: %s" % (last_employee_user_id))

            self.logger.debug("[JD]构建转发信息")
            yield self._make_share_info(position_info, company_info)

            self.logger.debug("[JD]构建HR头像及底部转发文案")
            endorse = yield self._make_endorse_info(position_info, company_info)

            # 是否超出投递上限。每月每家公司一个人只能申请3次
            self.logger.debug("[JD]处理投递上限")
            can_apply = yield self.application_ps.is_allowed_apply_position(
                self.current_user.sysuser.id, company_info.id)

            # 相似职位推荐
            self.logger.debug("[JD]构建相似职位推荐")
            recomment_positions_res = yield self.position_ps.get_recommend_positions(position_id)

            header = self._make_json_header(
                position_info, company_info, star, application, endorse,
                can_apply, team.id, did)
            module_job_description = self._make_json_job_description(position_info)
            module_job_need = self._make_json_job_need(position_info)
            module_feature = self._make_json_job_feature(position_info)
            module_position_recommend = self._make_recommend_positions(recomment_positions_res)

            position_data = ObjectDict()
            add_item(position_data, "header", header)
            add_item(position_data, "module_job_description", module_job_description)
            add_item(position_data, "module_job_need", module_job_need)
            add_item(position_data, "module_feature", module_feature)
            add_item(position_data, "module_position_recommend", module_position_recommend)

            # 构建老微信样式所需要的数据
            self.logger.debug("[JD]是否显示新样式: {}".format(self.current_user.wechat.show_new_jd))
            if not self.current_user.wechat.show_new_jd:
                module_job_require_old = self._make_json_job_require_old(position_info)
                module_department_old = self._make_json_job_department(position_info)
                module_job_attr_old = self._make_json_job_attr(position_info)
                module_hr_register_old = self.current_user.wechat.hr_register & True

                add_item(position_data, "module_job_require", module_job_require_old)
                add_item(position_data, "module_department", module_department_old)
                add_item(position_data, "module_job_attr", module_job_attr_old)
                add_item(position_data, "module_hr_register", module_hr_register_old)

                # TODO 定制插入
                # 诺华定制
                # 代理投递
                self.render_page("position/info_old.html", data=position_data, meta_title=const.PAGE_POSITION_INFO)
            else:
                # [JD]职位所属团队及相关信息拼装
                module_job_require = self._make_json_job_require(position_info)
                module_company_info = self._make_json_job_company_info(company_info, did)
                self.logger.debug("[JD]构建团队相关信息")
                yield self._add_team_data(position_data, team,
                                          position_info.company_id, position_id)

                add_item(position_data, "module_company_info", module_company_info)
                add_item(position_data, "module_job_require", module_job_require)
                self.render_page("position/info.html", data=position_data, meta_title=const.PAGE_POSITION_INFO)

            # 后置操作
            # 红包处理
            if self.is_platform and self.current_user.recom:
                self.logger.debug("[JD]红包处理")
                yield self.redpacket_ps.handle_red_packet_position_related(
                    self.current_user,
                    position_info,
                    redislocker=self.redis,
                    is_click=True,
                    psc=self.params.psc)

            self.logger.debug("[JD]更新职位浏览量")
            yield self._make_position_visitnum(position_info)

            self.logger.debug("[JD]转发积分操作")
            yield self._make_add_reward_click(
                position_info, last_employee_user_id)

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

        return encode_id(self.current_user.sysuser.id)

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

        link = make_url(
            path.POSITION_PATH.format(position_info.id),
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

    def _make_recommend_positions(self, positions):
        """处理相似职位推荐"""
        if not positions:
            return None

        data = []
        for item in positions:
            pos = ObjectDict()
            pos.title = item.get("job_title")
            pos.location = item.get("job_city", "")
            pos.salary = gen_salary(item.get("salary_top"), item.get("salary_bottom"))
            pos.link = make_url(path.POSITION_PATH.format(item.get("pid")), self.params,
                                escape=["pid", "keywords", "cities", "candidate_source", "employment_type", "salary",
                                "department", "occupations", "custom", "degree", "page_from", "page_size"])
            pos.company_logo = self.static_url(item.get("company_logo") or const.COMPANY_HEADIMG)
            data.append(pos)
            if len(data) > 2:
                break

        res = ObjectDict({"title": "相关职位推荐", "data": data}) if data else None

        return res

    def _make_json_header(self, position_info, company_info, star, application,
                          endorse, can_apply, team_id, did):
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
            "team": team_id,
            "did": did,
            "salary": position_info.salary,
            #"team": position_info.department.lower() if position_info.department else ""
        })

        return data

    def _make_json_job_description(self, position_info):
        """构造职位描述"""
        if not position_info.accountabilities:
            data = None
        else:
            data = ObjectDict({
                "data": position_info.accountabilities,
            })

        return data

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
        return data

    def _make_json_job_need(self, position_info):
        """构造职位要求"""

        if not position_info.requirement:
            data = None
        else:
            data = ObjectDict({
                "data": position_info.requirement,
            })

        return data

    def _make_json_job_feature(self, position_info):
        """构造职位福利特色"""
        if not position_info.feature:
            data = None
        else:
            data = ObjectDict({
                "data": position_info.feature,
            })

        return data

    def _make_json_job_company_info(self, company_info, did):
        """构造职位公司信息"""
        data = ObjectDict({
            "icon_url": self.static_url(company_info.logo),
            "name": company_info.abbreviation or company_info.name,
            "description": company_info.slogan,
            "did": did,
        })

        return data

    def _make_json_job_require_old(self, position_info):
        """构造老微信样式的职位要求"""
        require = []

        if position_info.degree:
            require.append(["学历", position_info.degree])
        if position_info.experience:
            require.append(["工作经验", position_info.experience])
        if position_info.language:
            require.append(["语言要求", position_info.language])

        if len(require) == 0:
            data = None
        else:
            data = ObjectDict({
                "data":  require
            })
        return data

    def _make_json_job_department(self, position_info):
        """构造老微信的所属部门，自定义职能，自定义属性"""
        data = ObjectDict({
            "department_name": position_info.department,
            "occupation_name": position_info.employment_type,
            "custom_name": position_info.job_occupation,
        })

        return data

    def _make_json_job_attr(self, position_info):
        """构造老微信的职位属性"""
        data = ObjectDict({
            "job_type": position_info.candidate_source,
            "work_type": position_info.employment_type,
        })

        return data

    @gen.coroutine
    def _make_refresh_share_chain(self, position_info):
        """构造刷新链路"""

        last_employee_user_id = 0

        if self.current_user.recom:
            yield self._make_share_record(
                position_info, recom_user_id=self.current_user.recom.id)

            # 需要实时算出链路数据
            def get_psc():
                """获取 query 中的 psc (parent share chain id)
                返回 int 类型"""
                ret = 0
                try:
                    ret = int(self.params.psc) if self.params.psc else 0
                except ValueError:
                    pass
                finally:
                    return ret

            if position_info.status == 0:
                inserted_share_chain_id = yield self._refresh_share_chain(
                    presentee_user_id=self.current_user.sysuser.id,
                    position_id=position_info.id,
                    last_psc=get_psc())
                self.logger.debug(
                    "[JD]inserted_share_chain_id: %s" % inserted_share_chain_id)

                if inserted_share_chain_id:
                    self.params.update(psc=str(inserted_share_chain_id))

            last_employee_user_id = yield self.sharechain_ps.get_referral_employee_user_id(
                self.current_user.sysuser.id, position_info.id)

        yield self.position_ps.send_candidate_view_position(params={
            "user_id": self.current_user.sysuser.id,
            "position_id": position_info.id,
            "from_employee": 1 if last_employee_user_id else 0,
        })

        raise gen.Return(last_employee_user_id)

    @gen.coroutine
    def _make_share_record(self, position_info, recom_user_id):
        """插入 position share record 的原子操作"""
        params = ObjectDict()
        params.wechat_id = self.current_user.wechat.id
        params.viewer_id = 0
        params.viewer_ip = self.request.remote_ip
        params.source = 0 if self.is_platform else 1
        params.click_from = wx.CLICK_FROM.get(
            self.get_argument("from", ""), 0)

        params.presentee_id = self.current_user.wxuser.id or 0
        params.presentee_user_id = self.current_user.sysuser.id
        params.position_id = position_info.id
        params.recom_user_id = recom_user_id

        recom_wx_user = yield self.user_ps.get_wxuser_unionid_wechat_id(
            unionid=self.current_user.recom.unionid,
            wechat_id=self.current_user.wechat.id
        )
        params.recom_id = recom_wx_user.id or 0

        yield self.sharechain_ps.create_share_record(params)

    @gen.coroutine
    def _refresh_share_chain(self,
                             presentee_user_id,
                             position_id,
                             last_psc=None):
        """刷新链路的原子操作"""
        inserted_share_chain_id = yield self.sharechain_ps.refresh_share_chain(
            presentee_user_id=presentee_user_id,
            position_id=position_id,
            share_chain_parent_id=last_psc
        )
        raise gen.Return(inserted_share_chain_id)

    @gen.coroutine
    def _redirect_when_recom_is_openid(self, position_info):
        """当recom是openid时，刷新链路，改变recom的值，跳转"""
        def recom_is_like_openid():
            return (self.params.recom and
                    self.params.recom.startswith('o') and
                    not str(self.params.recom).isdigit())

        if recom_is_like_openid():
            recom_wxuser = yield self.user_ps.get_wxuser_openid_wechat_id(
                openid=self.params.recom,
                wechat_id=self.current_user.wechat.id)
            replace_query = dict(recom=encode_id(recom_wxuser.sysuser_id))

            psc = yield self.sharechain_ps.find_last_psc(
                position_id=position_info.id,
                presentee_user_id=recom_wxuser.sysuser_id)
            if psc:
                replace_query.update(psc=psc)

            redirect_url = url_append_query(self.fullurl, **replace_query)
            self.redirect(redirect_url)

    @gen.coroutine
    def _make_add_reward_click(self, position_info, recom_employee_user_id):
        """给员工加积分"""

        if (not self.current_user.employee and
            recom_employee_user_id != self.current_user.sysuser.id and
            self.is_platform):

            recom_employee = yield self.user_ps.get_valid_employee_by_user_id(
                recom_employee_user_id)

            if recom_employee and recom_employee.wxuser_id:
                res = yield self.position_ps.add_reward_for_recom_click(
                    employee=recom_employee,
                    company_id=self.current_user.company.id,
                    berecom_wxuser_id=self.current_user.wxuser.id or 0,
                    berecom_user_id=self.current_user.sysuser.id,
                    position_id=position_info.id)

                self.logger.debug("[JD]给员工加积分： %s" % res)
            else:
                self.logger.warning(
                    "[JD]给员工加积分异常：员工不存在或员工 wxuser_id 不存在: %s" %
                    recom_employee)

    @gen.coroutine
    def _make_send_publish_template(self, position_info):
        """浏览量达到5次后，向 HR 发布模板消息
        注：只向 HR 平台发布的职位发送模板消息，ATS 同步的职位不发送"""

        if position_info.visitnum == 4 and position_info.source == 0:
            help_wechat = yield self.wechat_ps.get_wechat(conds={
                "signature": self.settings.helper_signature
            })

            hr_account, hr_wx_user = yield self._make_hr_info(
                position_info.publisher)

            if hr_wx_user.openid:
                # 如果企业有公众号，发企业链接，若无，发集合号链接
                if self.current_user.wechat:
                    link = make_url(
                        path.POSITION_PATH.format(position_info.id),
                        host=self.settings.platform_host,
                        wechat_signature=self.current_user.wechat.signature)
                else:
                    link = make_url(path.OLD_POSITION_PATH,
                                    host=self.settings.qx_host, m="info",
                                    pid=position_info.id)

                yield position_view_five(help_wechat.id, hr_wx_user.openid,
                                         link, position_info.title,
                                         position_info.salary)

    @gen.coroutine
    def _add_team_data(self, position_data, team, company_id, position_id):

        if team:
            company_config = COMPANY_CONFIG.get(company_id)
            module_team_position = yield self._make_team_position(
                team, position_id, company_id)
            if module_team_position:
                add_item(position_data, "module_team_position",
                         module_team_position)

            if team.is_show:
                module_mate_day = yield self._make_mate_day(team)
                if module_mate_day:
                    add_item(position_data, "module_mate_day", module_mate_day)

                if not company_config.no_jd_team:
                    module_team = yield self._make_team(team)
                    add_item(position_data, "module_team", module_team)

    @gen.coroutine
    def _make_team_position(self, team, position_id, company_id):
        """团队职位，构造数据"""
        res = yield self.position_ps.get_team_position(
            team.name, self.params, position_id, company_id)
        raise gen.Return(res)

    @gen.coroutine
    def _make_mate_day(self, team):
        """同事的一天，构造数据"""
        res = yield self.position_ps.get_mate_data(team.jd_media)
        raise gen.Return(res)

    @gen.coroutine
    def _make_team(self, team):
        """所属团队，构造数据"""
        more_link = make_url(path.TEAM_PATH.format(team.id), self.params),
        res = yield self.position_ps.get_team_data(team, more_link)
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
