# coding=utf-8

from tornado import gen

import conf.common as const
import conf.message as msg
import conf.path as path
import conf.platform as const_platform
import conf.wechat as wx
from handler.base import BaseHandler
from tests.dev_data.user_company_config import COMPANY_CONFIG
from util.common import ObjectDict
from util.common.exception import MyException
from util.common.cipher import encode_id
from util.common.decorator import handle_response, check_employee, NewJDStatusCheckerAddFlag, authenticated, log_time
from util.common.mq import award_publisher
from util.tool.str_tool import gen_salary, add_item, split, gen_degree_v2, gen_experience_v2, languge_code_from_ua
from util.tool.url_tool import url_append_query
from util.wechat.template import position_view_five_notice_tpl, position_share_notice_employee_tpl
from util.common.decorator import log_time


class PositionHandler(BaseHandler):
    @log_time
    @handle_response
    @NewJDStatusCheckerAddFlag()
    @authenticated
    @gen.coroutine
    def get(self, position_id):
        """显示 JD 页
        """
        position_info = yield self.position_ps.get_position(position_id)

        if position_info.id and position_info.company_id == self.current_user.company.id:
            yield self._redirect_when_recom_is_openid(position_info)
            if self.request.connection.stream.closed():
                return

            team = yield self.team_ps.get_team_by_id(position_info.team_id)
            position_info.team = team

            self.logger.debug("[JD]构建收藏信息")
            star = yield self.position_ps.is_position_stared_by(self.current_user.sysuser.id, position_id)

            self.logger.debug("[JD]构建申请信息")
            application = yield self.application_ps.get_application(position_id, self.current_user.sysuser.id)

            self.logger.debug("[JD]构建职位所属公司信息")
            did = yield self.company_ps.get_real_company_id(position_info.publisher, position_info.company_id)
            company_info = yield self.company_ps.get_company(conds={"id": did}, need_conf=True)

            # 刷新链路
            self.logger.debug("[JD]刷新链路")
            last_employee_user_id, last_employee_id = yield self._make_refresh_share_chain(position_info)
            self.logger.debug("[JD]last_employee_user_id: %s" % (last_employee_user_id))

            self.logger.debug("[JD]构建转发信息")
            yield self._make_share_info(position_info, company_info)

            self.logger.debug("[JD]构建HR头像及底部转发文案")
            endorse = yield self._make_endorse_info(position_info, company_info)

            # 是否超出投递上限。每月每家公司一个人只能申请3次
            self.logger.debug("[JD]处理投递上限")
            can_apply = yield self.application_ps.is_allowed_apply_position(
                self.current_user.sysuser.id, company_info.id, position_id)

            # 相似职位推荐
            self.logger.debug("[JD]构建相似职位推荐")
            recomment_positions_res = yield self.position_ps.get_recommend_positions(position_id)

            # 获取公司配置信息
            teamname_custom = self.current_user.company.conf_teamname_custom

            header = yield self._make_json_header(
                position_info, company_info, star, application, endorse,
                can_apply, team.id if team else 0, did, teamname_custom)
            module_job_description = self._make_json_job_description(position_info)
            module_job_need = self._make_json_job_need(position_info)
            position_feature = yield self.position_ps.get_position_feature(position_id)
            module_feature = self._make_json_job_feature(position_feature)

            module_position_recommend = self._make_recommend_positions(self.locale, recomment_positions_res)

            position_data = ObjectDict()
            add_item(position_data, "header", header)
            add_item(position_data, "module_job_description", module_job_description)
            add_item(position_data, "module_job_need", module_job_need)
            add_item(position_data, "module_feature", module_feature)
            add_item(position_data, "module_position_recommend", module_position_recommend)

            # 构建老微信样式所需要的数据
            self.logger.debug("[JD]是否显示新样式: {}".format(self.current_user.company.conf_newjd_status))
            # 0是未开启，1是用户申请开启，2是审核通过（使用新jd），3撤销（返回基础版）
            # added in NewJDStatusCheckerAddFlag
            if self.flag_should_display_newjd:
                # 正常开启或预览
                # [JD]职位所属团队及相关信息拼装
                module_job_attr_v2 = self._make_json_job_attr_v2(position_info)
                module_job_require = self._make_json_job_require(position_info)
                module_company_info = self._make_json_job_company_info(company_info, did)
                self.logger.debug("[JD]构建团队相关信息")
                yield self._add_team_data(position_data, team,
                                          position_info.company_id, position_id, teamname_custom)

                add_item(position_data, "module_job_attr", module_job_attr_v2)
                add_item(position_data, "module_company_info", module_company_info)
                add_item(position_data, "module_job_require", module_job_require)
                self.render_page(
                    "position/info.html",
                    data=position_data,
                    meta_title=const.PAGE_POSITION_INFO)
            else:
                # 老样式
                module_job_require_old = self._make_json_job_require_old(position_info)
                module_department_old = self._make_json_job_department(position_info)
                module_job_attr_old = self._make_json_job_attr(position_info)
                module_hr_register_old = int(self.current_user.wechat.hr_register) & True
                module_cmp_impression = self._make_json_company_impression(company_info)

                add_item(position_data, "module_job_require", module_job_require_old)
                add_item(position_data, "module_department", module_department_old)
                add_item(position_data, "module_job_attr", module_job_attr_old)
                add_item(position_data, "module_hr_register", module_hr_register_old)
                add_item(position_data, "module_company_impression", module_cmp_impression)

                # 定制化 start
                # 诺华定制
                suppress_apply = yield self.customize_ps.get_suppress_apply(position_info)
                # 代理投递
                delegate_drop = yield self.customize_ps.get_delegate_drop(self.current_user.wechat,
                                                                          self.current_user.employee,
                                                                          self.params)
                add_item(position_data, "suppress_apply", suppress_apply)
                add_item(position_data, "delegate_drop", delegate_drop)
                # 定制化 end

                self.render_page(
                    "position/info_old.html",
                    data=position_data,
                    meta_title=const.PAGE_POSITION_INFO)

            self.flush()

            # 后置操作
            if self.is_platform and self.current_user.recom:
                # 转发积分
                if last_employee_user_id:
                    self.logger.debug("[JD]转发积分操作")

                    award_publisher.add_awards_click_jd(
                        company_id=position_info.company_id,
                        position_id=position_id,
                        employee_id=last_employee_id,
                        recom_user_id=last_employee_user_id,
                        be_recom_user_id=self.current_user.sysuser.id
                    )

                # 红包处理
                self.logger.debug("[JD]红包处理")
                yield self.redpacket_ps.handle_red_packet_position_related(
                    self.current_user,
                    position_info,
                    redislocker=self.redis,
                    is_click=True,
                    psc=self.params.psc)

            self.logger.debug("[JD]更新职位浏览量")
            yield self._make_position_visitnum(position_info)

            # 浏览量达到5次后，向 HR 发布模板消息
            yield self._make_send_publish_template(position_info)

        else:
            self.write_error(404)
            return

    @log_time
    @gen.coroutine
    def _make_position_visitnum(self, position_info):
        """更新职位浏览量"""
        yield self.position_ps.update_position(conds={
            "id": position_info.id
        }, fields={
            "visitnum": position_info.visitnum + 1,
            "update_time": position_info.update_time_ori,
        })

    @gen.coroutine
    def _make_share_info(self, position_info, company_info):
        """构建 share 内容"""

        # 如果有红包，则取红包的分享文案
        red_packet = yield self.redpacket_ps.get_last_running_hongbao_config_by_position(position_info)

        if red_packet:
            cover = self.share_url(red_packet.share_img)
            title = "{} {}".format(position_info.title, red_packet.share_title)
            description = "".join(split(red_packet.share_desc))
        else:
            cover = self.share_url(company_info.logo)
            title = position_info.title
            description = self.locale.translate(msg.SHARE_DES_DEFAULT)

            if position_info.share_tpl_id:
                if position_info.share_tpl_id > 3:
                    if position_info.share_title:
                        title = position_info.share_title
                    if position_info.share_description:
                        description = position_info.share_description
                else:
                    share_tpl_id = position_info.share_tpl_id
                    title = self.locale.translate('share_tpl_title%s' % share_tpl_id).format(company_info.abbreviation,
                                                                                             position_info.title)
                    description = self.locale.translate('share_tpl_description%s' % share_tpl_id)

        link = self.make_url(
            path.POSITION_PATH.format(position_info.id),
            self.params,
            recom=self.position_ps._make_recom(self.current_user.sysuser.id),
            escape=["pid", "keywords", "cities", "candidate_source",
                    "employment_type", "salary", "department", "occupations",
                    "custom", "degree", "page_from", "page_size"]
        )

        self.params.share = ObjectDict({
            "cover": cover,
            "title": title,
            "description": description,
            "link": link,
            "pid": position_info.id,
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

        hr_name = hr_account.username or hr_wx_user.nickname or ''
        company_name = company_info.abbreviation or company_info.company_name or ''

        is_hr = (self.current_user.qxuser.unionid is not None
                 and self.current_user.qxuser.unionid == hr_wx_user.unionid)

        endorse = ObjectDict({
            "publisher": position_info.publisher,
            "is_hr": is_hr,
            "avatar": self.static_url(hrheadimgurl),
            "name": hr_name,
            "company": company_name,
            "department": position_info.department
        })

        self.logger.debug("_make_endorse_info: {}".format(endorse))

        raise gen.Return(endorse)

    def _make_recommend_positions(self, locale, positions):
        """处理相似职位推荐"""
        if not positions:
            return None

        data = []
        for item in positions:
            pos = ObjectDict()
            pos.title = item.get("job_title")
            pos.location = item.get("job_city", "")
            pos.salary = gen_salary(
                item.get("salary_top"),
                item.get("salary_bottom"))
            pos.link = self.make_url(
                path.POSITION_PATH.format(
                    item.get("pid")),
                self.params,
                escape=[
                    "pid",
                    "keywords",
                    "cities",
                    "candidate_source",
                    "employment_type",
                    "salary",
                    "department",
                    "occupations",
                    "custom",
                    "degree",
                    "page_from",
                    "page_size"])
            pos.company_logo = self.static_url(
                item.get("company_logo") or const.COMPANY_HEADIMG)
            data.append(pos)
            if len(data) > 2:
                break

        res = ObjectDict({"title": locale.translate("jd_more_jobs"), "data": data}) if data else None

        return res

    @log_time
    @gen.coroutine
    def _make_json_header(self, position_info, company_info, star, application,
                          endorse, can_apply, team_id, did, teamname_custom):
        """构造头部 header 信息"""

        # 获得母公司配置信息
        parent_company_info = yield self._make_parent_company_info()

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
            "hr_chat": bool(parent_company_info.conf_hr_chat),
            "teamname_custom": teamname_custom["teamname_custom"],
            "candidate_source": position_info.candidate_source_num
            # "team": position_info.department.lower() if position_info.department else ""
        })

        return data

    @gen.coroutine
    def _make_parent_company_info(self):
        """获得母公司的配置信息，部分逻辑由母公司控制，例如开启 IM 聊天，开启新微信"""
        parent_company_info = yield self.company_ps.get_company(conds={
            "id": self.current_user.wechat.company_id
        }, need_conf=True)

        return parent_company_info

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
            require.append("{0} {1}".format(
                self.locale.translate('jd_degree'),
                gen_degree_v2(position_info.raw_degree,
                              position_info.raw_degree_above, self.locale)
            ))

        if position_info.experience:
            require.append("{0} {1}".format(
                self.locale.translate('jd_work_exp'),
                gen_experience_v2(position_info.raw_experience,
                                  position_info.raw_experience_above,
                                  self.locale)))

        if position_info.language:
            require.append("{0} {1}".format(
                self.locale.translate('jd_language'),
                position_info.language))

        if (position_info.management_experience and
                    position_info.management_experience == 'common_need'):
            require.append("{0} {1}".format(
                self.locale.translate('jd_management_exp'),
                self.locale.translate(position_info.management_experience)))

        if len(require) == 0:
            data = None
        else:
            data = ObjectDict({"data": require})

        return data

    def _make_json_job_attr_v2(self, position_info):
        """构造新JD的职位属性"""

        attr = []

        if position_info.candidate_source:
            attr.append("招聘类型 {0}".format(
                self.locale.translate(position_info.candidate_source)))

        if position_info.employment_type:
            attr.append("工作性质 {0}".format(
                self.locale.translate(position_info.employment_type)))

        if self.current_user.company.conf_job_occupation and position_info.job_occupation:
            attr.append("{} {}".format(self.current_user.company.conf_job_occupation, position_info.job_occupation))

        if self.current_user.company.conf_job_custom_title and position_info.job_custom:
            attr.append("{} {}".format(self.current_user.company.conf_job_custom_title, position_info.job_custom))

        if not attr:
            data = None
        else:
            data = ObjectDict({
                "data": attr
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

    def _make_json_job_feature(self, position_feature):
        """构造职位福利特色"""
        feature = []
        if not position_feature:
            data = None
        else:
            for f in position_feature:
                feature.append(f['feature'])
            data = ObjectDict({
                "data": feature
            })
        return data

    def _make_json_job_company_info(self, company_info, did):
        """构造职位公司信息"""
        data = ObjectDict({
            "icon_url": self.static_url(company_info.logo),
            "name": company_info.abbreviation or company_info.name,
            "description": company_info.slogan,
            "did": did if did != self.current_user.company.id else "",  # 主公司不需要提供 did
        })

        return data

    def _make_json_job_require_old(self, position_info):
        """构造老微信样式的职位要求"""
        require = []

        if position_info.degree:
            require.append([self.locale.translate('jd_degree'),
                            gen_degree_v2(position_info.raw_degree, position_info.raw_degree_above, self.locale)])

        if position_info.experience:
            require.append([
                self.locale.translate('jd_work_exp'),
                gen_experience_v2(position_info.raw_experience,
                                  position_info.raw_experience_above,
                                  self.locale)
            ])

        if position_info.language:
            require.append([self.locale.translate('jd_language'), position_info.language])

        if len(require) == 0:
            data = None
        else:
            data = ObjectDict({
                "data": require
            })
        return data

    def _make_json_company_impression(self, company_info):
        """构造老微信样式的企业印象"""

        if company_info.impression:
            if len(company_info.impression) == 0:
                data = None
            else:
                data = ObjectDict({
                    "data": company_info.impression
                })
        else:
            data = None
            self.logger.warning("Warning: don't have company_info.impression")
        return data

    def _make_json_job_department(self, position_info):
        """构造老微信的所属部门，自定义职能，自定义属性"""
        data = ObjectDict({
            "department_name": position_info.team.name,
            "occupation_name": position_info.job_occupation,
            "custom_name": position_info.job_custom,
        })

        return data

    def _make_json_job_attr(self, position_info):
        """构造老微信的职位属性"""
        data = ObjectDict({
            "job_type": self.locale.translate(position_info.candidate_source),
            "work_type": self.locale.translate(position_info.employment_type)
        })

        return data

    @log_time
    @gen.coroutine
    def _make_refresh_share_chain(self, position_info):
        """构造刷新链路"""

        last_employee_user_id = 0
        last_employee_id = 0
        inserted_share_chain_id = 0

        if self.current_user.recom and self.current_user.sysuser:
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
                    "[JD]inserted_share_chain_id: %s" %
                    inserted_share_chain_id)

                if inserted_share_chain_id:
                    self.params.update(psc=str(inserted_share_chain_id))

            last_employee_user_id = yield self.sharechain_ps.get_referral_employee_user_id(
                self.current_user.sysuser.id, position_info.id)

            if last_employee_user_id:
                _, employee_info = yield self.employee_ps.get_employee_info(
                    user_id=last_employee_user_id,
                    company_id=self.current_user.company.id
                )
                if employee_info:
                    last_employee_id = employee_info.id

        if self.current_user.sysuser.id:
            yield self.candidate_ps.send_candidate_view_position(
                user_id=self.current_user.sysuser.id,
                position_id=position_info.id,
                sharechain_id=inserted_share_chain_id,
            )

        return last_employee_user_id, last_employee_id

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
    def _refresh_share_chain(self, presentee_user_id, position_id, last_psc=None):
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
                replace_query.update({'psc': psc})

            redirect_url = url_append_query(self.fullurl(), **replace_query)
            self.redirect(redirect_url)
            return

    @log_time
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
                # 如果企业有公众号，发企业链接，若无，发聚合号链接
                if self.current_user.wechat:
                    link = self.make_url(
                        path.POSITION_PATH.format(position_info.id),
                        wechat_signature=self.current_user.wechat.signature)
                else:
                    link = self.make_url(path.GAMMA_POSITION_HOME.format(position_info.id))

                yield position_view_five_notice_tpl(help_wechat.id, hr_wx_user.openid,
                                                    link, position_info.title,
                                                    position_info.salary)

    @gen.coroutine
    def _add_team_data(self, position_data, team, company_id, position_id, teamname_custom):

        if team:
            module_team_position = yield self._make_team_position(
                team, position_id, company_id, teamname_custom)
            if module_team_position:
                add_item(position_data, "module_team_position",
                         module_team_position)

            # [hr3.4]team.is_show只是用来判断是否在团队列表显示
            cms_page = yield self._make_cms_page(team.id)
            if cms_page:
                add_item(position_data, "module_mate_day", cms_page)
                # 玛氏定制
                company_config = COMPANY_CONFIG.get(company_id)
                if (
                    company_config and not company_config.no_jd_team) or not company_config:  # 不在职位详情页展示所属团队, 目前只有Mars有这个需求,
                    module_team = yield self._make_team(team, teamname_custom)
                    add_item(position_data, "module_team", module_team)
            else:
                module_team = yield self._make_team(team, teamname_custom)
                if module_team:
                    add_item(position_data, "module_mate_day", module_team)

    @gen.coroutine
    def _make_team_position(self, team, position_id, company_id, teamname_custom):
        """团队职位，构造数据"""
        res = yield self.position_ps.get_team_position(
            self.locale, team.id, self.params, position_id, company_id,
            teamname_custom)
        raise gen.Return(res)

    @gen.coroutine
    def _make_cms_page(self, team_id):
        res = yield self.position_ps.get_cms_page(team_id)
        return res

    @gen.coroutine
    def _make_team(self, team, teamname_custom):
        """所属团队，构造数据"""
        more_link = team.link if team.link else self.make_url(path.TEAM_PATH.format(team.id), self.params)
        res = yield self.position_ps.get_team_data(team, more_link, teamname_custom)
        raise gen.Return(res)


class PositionListInfraParamsMixin(BaseHandler):

    def make_position_list_infra_params(self):
        """构建调用基础服务职位列表的 params"""

        infra_params = ObjectDict()

        infra_params.company_id = self.current_user.company.id

        if self.params.did:
            infra_params.did = self.params.did

        start_count = (int(self.params.get("count", 0)) *
                       const_platform.POSITION_LIST_PAGE_COUNT)

        infra_params.page_from = start_count
        infra_params.page_size = const_platform.POSITION_LIST_PAGE_COUNT

        if self.params.salary:
            k = str(self.params.salary)
            try:
                infra_params.salary = "%d,%d" % (
                    const_platform.SALARY[const_platform.SALARY_NAME_TO_INDEX[k]].salary_bottom,
                    const_platform.SALARY[const_platform.SALARY_NAME_TO_INDEX[k]].salary_top)
            except KeyError:  # 如果用户自行修改了 GET 参数，不至于报错
                infra_params.salary = ""

        if self.params.degree:
            infra_params.degree = self.params.degree
        else:
            infra_params.degree = ""

        # 招聘类型和职位性质接受兼容 数字编号 中文
        if self.params.candidate_source:
            infra_params.candidate_source = const.CANDIDATE_SOURCE_SEARCH.get(self.params.candidate_source, "") \
                if self.params.candidate_source.isdigit() else self.params.candidate_source
        else:
            infra_params.candidate_source = ""

        if self.params.employment_type:
            infra_params.employment_type = const.EMPLOYMENT_TYPE_SEARCH.get(self.params.employment_type, "") \
                if self.params.employment_type.isdigit() else self.params.employment_type
        else:
            infra_params.employment_type = ""

        infra_params.update(
            keywords=self.params.keyword if self.params.keyword else "",
            cities=self.params.city if self.params.city else "",
            department=self.params.team_name if self.params.team_name else "",
            occupations=self.params.occupation if self.params.occupation else "",
            custom=self.params.custom if self.params.custom else "",
            order_by_priority=True)

        self.logger.debug("[position_list_infra_params]: %s" % infra_params)

        return infra_params


class PositionListDetailHandler(PositionListInfraParamsMixin, BaseHandler):
    """获取职位列表"""

    @handle_response
    @check_employee
    @gen.coroutine
    def get(self):

        infra_params = self.make_position_list_infra_params()

        useragent = self.request.headers.get('User-Agent')
        lang_from_ua = languge_code_from_ua(useragent)
        # 校验一下可能出现的参数：
        # hb_c: 红包活动id
        # did: 子公司id
        hb_c = 0
        if self.params.hb_c and self.params.hb_c.isdigit():
            hb_c = int(self.params.hb_c)

        recom_push_id = 0
        if self.params.recom_push_id and self.params.recom_push_id.isdigit():
            recom_push_id = int(self.params.recom_push_id)

        if recom_push_id and hb_c:
            raise MyException("错误的链接")

        if hb_c:
            # 红包职位列表
            infra_params.update(hb_config_id=hb_c)
            position_list = yield self.position_ps.infra_get_rp_position_list(infra_params)

        elif recom_push_id:
            # 员工推荐列表
            if int(self.params.get("count", 0)) == 0:
                position_list = yield self.get_employee_position_list(recom_push_id, infra_params)
            else:
                position_list = []

        else:
            # 普通职位列表
            position_list = yield self.position_ps.infra_get_position_list(infra_params)

            # 获取获取到普通职位列表，则根据获取的数据查找其中红包职位的红包相关信息
            rp_position_list = list(self.__rp_position_generator(position_list))

            if position_list and rp_position_list:
                rpext_list = yield self.position_ps.infra_get_position_list_rp_ext(rp_position_list)

                for position in position_list:
                    pext = [e for e in rpext_list if e.pid == position.id]
                    if pext:
                        position.remain = pext[0].remain
                        position.employee_only = pext[0].employee_only
                        position.is_rp_reward = position.remain > 0
                    else:
                        position.is_rp_reward = False

        position_id_list = list()
        for e in position_list:
            position_id_list.append(e.id)

        # 获取当前职位列表中用户已感兴趣职位列表
        fav_position_id_list = yield self.usercenter_ps.get_user_position_stared_list(
            self.current_user.sysuser.id, position_id_list
        )

        # 获取用户已申请职位列表
        applied_application_id_list = yield self.usercenter_ps.get_applied_applications_list(self.current_user.sysuser.id, position_id_list)

        # 诺华定制
        suppress_apply = yield self.customize_ps.is_suppress_apply_company(infra_params.company_id)

        position_custom_list = []
        position_custom_id_list = []
        if suppress_apply:
            position_custom_list, position_custom_id_list = yield self.position_ps.get_position_custom_list(position_id_list)

        # 是否达到投递上线
        social_res, school_res = yield self.application_ps.get_application_apply_status(self.current_user.sysuser.id, self.current_user.company.id)
        total_count = 0
        # 职位信息
        position_ex_list = list()
        for pos in position_list:
            position_ex = ObjectDict()
            position_ex["id"] = pos.id
            position_ex["priority"] = pos.priority
            position_ex["title"] = pos.title
            position_ex["visitnum"] = pos.visitnum
            position_ex["abbreviation"] = pos.abbreviation
            position_ex["department"] = pos.department
            position_ex["province"] = pos.province
            position_ex["salary"] = pos.salary
            position_ex["logo"] = pos.logo
            position_ex["company_name"] = pos.company_name
            position_ex["salary_top"] = pos.salary_top
            position_ex["salary_bottom"] = pos.salary_bottom
            position_ex["update_time"] = pos.update_time
            position_ex["rp_reward_amount"] = pos.rp_reward_amount
            position_ex["rp_reward_target"] = pos.rp_reward_target
            position_ex["company_abbr"] = pos.company_abbr
            position_ex["remain"] = pos.remain
            position_ex["publish_date"] = pos.publish_date
            position_ex["team_name"] = pos.team_name
            position_ex["job_description"] = pos.accountabilities
            position_ex["is_starred"] = pos.id in fav_position_id_list  # 判断职位收藏状态
            position_ex['is_applied'] = pos.id in applied_application_id_list  # 判断职位申请状态

            position_ex['candidate_source'] = pos.candidate_source
            position_ex['job_need'] = pos.requirement

            if lang_from_ua == "en_US":
                position_ex["city"] = pos.city_ename
                position_ex["salary"] = "Salary negotiable" if pos.salary == "薪资面议" else pos.salary
            else:
                position_ex["city"] = pos.city
                position_ex["salary"] = pos.salary
            total_count = pos.totalNum
            # 判断职位投递是否达到上限
            can_apply = False
            if pos.candidate_source:
                can_apply = school_res
            elif pos.candidate_source == 0:
                can_apply = social_res

            position_ex['can_apply'] = not can_apply
            # 判断是否显示红包
            is_employee = bool(self.current_user.employee)
            position_ex['has_reward'] = pos.is_rp_reward and (
                is_employee and pos.employee_only or not pos.employee_only)

            # 诺华定制
            position_ex['suppress_apply'] = ObjectDict()
            position_ex['suppress_apply']['is_suppress_apply'] = suppress_apply
            position_ex['suppress_apply']['job_number'] = pos.jobnumber
            if position_custom_list and position_custom_id_list and pos.id in position_custom_id_list:
                for custom in position_custom_list:
                    if pos.id == custom.id and custom.custom_field:
                        position_ex['suppress_apply']['custom_field'] = custom.custom_field
                    else:
                        position_ex['suppress_apply']['custom_field'] = ''

            position_ex_list.append(position_ex)

        self.send_json_success(
            data=ObjectDict(list=position_ex_list,
                            total_count=total_count)
        )

    @staticmethod
    def __rp_position_generator(position_list):
        for position in position_list:
            if isinstance(position, dict) and position.in_hb:
                yield position

    @gen.coroutine
    def get_employee_position_list(self, recom_push_id, params):
        """
        获取员工推荐职位列表
        :return:
        """
        company_id = self.current_user.company.id

        infra_params = ObjectDict({
            "companyId": company_id,
            "recomPushId": recom_push_id,
            "type": 1,  # hard code, 1表示员工
            "page_from": int(self.params.get("count", 0)/10) + 1,
            "page_size": params.page_size
        })

        position_list = yield self.position_ps.infra_get_position_employeerecom(infra_params, company_id)
        return position_list

    def get_search_filter_num(self):
        """get search filter number for statistics"""
        ret = 0
        if self.is_platform:
            self.params.pop("page_from", None)
            self.params.pop("page_size", None)
            self.params.pop("order_by_priority", None)
            for k, v in self.params.items():
                if v:
                    ret += 1


class PositionEmpNoticeHandler(BaseHandler):
    @handle_response
    @gen.coroutine
    def get(self):
        """
        职位相关转发后的回调。10分钟后发送模板消息
        :return:
        """
        if not self.current_user.employee or not self.params.pid:
            self.send_json_success()
            return

        position = yield self.position_ps.get_position(self.params.pid)

        link = self.make_url(path.EMPLOYEE_RECOMMENDS, wechat_signature=self.current_user.wechat.signature)

        if self.current_user.wechat.passive_seeker == const.OLD_YES:
            yield position_share_notice_employee_tpl(self.current_user.company.id,
                                                     position.title,
                                                     position.salary,
                                                     self.current_user.sysuser.id,
                                                     self.params.pid,
                                                     link)

        self.send_json_success()


class PositionListHandler(PositionListInfraParamsMixin, BaseHandler):
    @handle_response
    @check_employee
    @gen.coroutine
    def get(self):
        """获取职位列表页"""

        infra_params = self.make_position_list_infra_params()

        # 校验一下可能出现的参数：
        # hb_c: 红包活动id
        # did: 子公司id
        hb_c = 0
        if self.params.hb_c and self.params.hb_c.isdigit():
            hb_c = int(self.params.hb_c)

        did = 0
        if self.params.did and self.params.did.isdigit():
            did = int(self.params.did)

        recom_push_id = 0
        if self.params.recom_push_id and self.params.recom_push_id.isdigit():
            recom_push_id = int(self.params.recom_push_id)

        if recom_push_id and hb_c:
            raise MyException("错误的链接")

        if hb_c:
            # 红包职位分享
            infra_params.update(hb_config_id=hb_c)
            rp_share_info = yield self.position_ps.infra_get_rp_share_info(infra_params)
            yield self._make_share_info(self.current_user.company.id, did, rp_share_info)
        else:
            yield self._make_share_info(self.current_user.company.id, did)

        # 只渲染必要的公司信息
        yield self.make_company_info()

        position_title = self.locale.translate(const_platform.POSITION_LIST_TITLE_DEFAULT)
        if self.params.recomlist or self.params.noemprecom:
            position_title = self.locale.translate(const_platform.POSITION_LIST_TITLE_RECOMLIST)

        teamname_custom = self.current_user.company.conf_teamname_custom.teamname_custom

        if self.locale.code == 'zh_CN':
            teamname_custom = self.locale.translate(
                teamname_custom, plural_message=teamname_custom, count=2)

        elif self.locale.code == 'en_US':
            teamname_custom = self.locale.translate(
                '团队', plural_message='团队', count=2)

        company = ObjectDict()
        company['id'] = self.params.company.id
        company['logo'] = self.params.company.logo
        company['abbreviation'] = self.params.company.abbreviation
        company['industry'] = self.params.company.industry
        company['scale_name'] = self.params.company.scale_name
        company['banner'] = self.params.company.banner

        self.render_page(
            template_name="position/index.html",
            meta_title=position_title,
            data=ObjectDict(
                company=company,
                use_neowx=bool(self.current_user.company.conf_newjd_status == 2),
                teamname_custom=teamname_custom)
        )

    @gen.coroutine
    def make_company_info(self):
        """只提取必要的company信息用于渲染"""
        if self.params.did:
            company = yield self.company_ps.get_company(
                conds={'id': self.params.did}, need_conf=True)
            if not company.banner:
                parent_company = self.current_user.company
                company.banner = parent_company.banner
        else:
            company = self.current_user.company
        self.params.company = self.position_ps.limited_company_info(company)

    @gen.coroutine
    def _make_share_info(self, company_id, did=None, rp_share_info=None):
        """构建 share 内容"""

        company_info = yield self.company_ps.get_company(
            conds={"id": did or company_id}, need_conf=True)

        if not rp_share_info:
            escape = ["recomlist"]
            cover = self.share_url(company_info.logo)
            title = company_info.abbreviation + self.locale.translate('job_hotjobs')
            description = self.locale.translate(msg.SHARE_DES_DEFAULT)

        else:
            cover = self.share_url(rp_share_info.cover)
            escape = [
                "pid", "keywords", "cities", "candidate_source",
                "employment_type", "salary", "department", "occupations",
                "custom", "degree", "page_from", "page_size"
            ]
            title = rp_share_info.title
            description = rp_share_info.description

        link = self.make_url(
            path.POSITION_LIST,
            self.params,
            recom=self.position_ps._make_recom(self.current_user.sysuser.id),
            escape=escape)

        self.params.share = ObjectDict({
            "cover": cover,
            "title": title,
            "description": description,
            "link": link
        })


class PositionListSugHandler(PositionListInfraParamsMixin, BaseHandler):
    @handle_response
    @check_employee
    @gen.coroutine
    def get(self):
        """
        sug搜索
        :return:
        """
        # todo:注释
        # sug = ObjectDict()
        # sug.list = []
        # return self.send_json_success(sug)

        infra_params = self.make_position_list_infra_params()
        sug = ObjectDict()
        # 获取五条sug数据
        infra_params.update(page_size=const_platform.SUG_LIST_COUNT,
                            keyWord=self.params.keyword if self.params.keyword else "",
                            page_from=int(self.params.get("count", 0)/10) + 1)
        res_data = yield self.position_ps.infra_obtain_sug_list(infra_params)
        suggest = res_data.get('suggest') if res_data else ''
        if suggest:
            sug.list = [e.get('title') for e in suggest]

        return self.send_json_success(sug)

