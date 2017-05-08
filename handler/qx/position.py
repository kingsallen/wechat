# coding=utf-8

# @Time    : 4/13/17 11:42
# @Author  : panda (panyuxin@moseeker.com)
# @File    : position.py
# @DES     : 聚合号职位详情页

from tornado import gen

from handler.base import BaseHandler
from util.common.decorator import handle_response
from util.common import ObjectDict
from util.tool.str_tool import split


class PositionHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self, position_id):

        position_info = yield self.position_ps.get_position(position_id)

        self.logger.debug("[JD]构建职位所属公司信息")
        did = yield self.company_ps.get_real_company_id(position_info.publisher, position_info.company_id)
        company_info = yield self.company_ps.get_company(conds={"id": did}, need_conf=True)

        self.logger.debug("position:{}".format(position_info))
        self.logger.debug("company:{}".format(company_info))

        if position_info.id and company_info.conf_show_in_qx:
            self.logger.debug("[JD]构建基础信息")
            jd_home = yield self._make_jd_home(position_info, company_info)

            self.logger.debug("[JD]构建详细信息")
            jd_detail = yield self._make_jd_detail(position_id, position_info, company_info)

            self.logger.debug("[JD]构建转发信息")
            # yield self._make_share_info(position_info, company_info)

            data = dict(jd_detail, **jd_home)
            self.send_json_success(data=data)
        else:
            self.write_error(404)
            return

    @gen.coroutine
    def _make_jd_home(self, position_info, company_info):

        team = yield self.team_ps.get_team_by_id(position_info.team_id)

        self.logger.debug("[JD]构建职位默认图")
        position = yield self.aggregation_ps.opt_es_position(position_info.id)
        self.logger.debug("position:{}".format(position))
        self.logger.debug("position.hits:{}".format(position.hits))
        self.logger.debug("position.hits[0]:{}".format(position.hits[0]))
        team_img, job_img, company_img = yield self.aggregation_ps.opt_jd_home_img(
            position.hits[0].get("_source").get("company", {}).get("industry_type"), position.hits[0])

        data = ObjectDict(
            id=position_info.id,
            title=position_info.title,
            salary=position_info.salary,
            team=team.name,
            team_id=team.id or 0,
            did=company_info.id,
            city=split(position_info.city, [",","，"]),
            degree=position_info.degree,
            experience=position_info.experience,
            team_img=team_img,
            job_img=job_img,
            company_img=company_img
        )

        return data

    @gen.coroutine
    def _make_jd_detail(self, position_id, position_info, company_info):

        company = ObjectDict(
            id=company_info.id,
            logo=self.static_url(company_info.logo),
            abbreviation=company_info.abbreviation,
        )

        self.logger.debug("[JD]构建收藏信息")
        star = yield self.position_ps.is_position_stared_by(self.current_user.sysuser.id, position_id)

        self.logger.debug("[JD]构建申请信息")
        application = yield self.application_ps.get_application(position_id, self.current_user.sysuser.id)

        # 是否超出投递上限。每月每家公司一个人只能申请3次
        self.logger.debug("[JD]处理投递上限")
        can_apply = yield self.application_ps.is_allowed_apply_position(
            self.current_user.sysuser.id, company_info.id)

        job_need = position_info.requirement or list()
        job_description = position_info.accountabilities or list()
        job_feature = position_info.feature or list()
        job_require = self.__make_json_job_require(position_info)

        data = ObjectDict(
            company=company,
            is_applied=bool(application),
            appid=application.id or 0,
            is_collected=star,
            can_apply=can_apply,
            job_need=job_need,
            job_description=job_description,
            job_feature=job_feature,
            job_require=job_require,
        )

        return data

    def __make_json_job_require(self, position_info):
        """构造职位要求"""

        require = ObjectDict()
        if position_info.language:
            require.update({"name": "语言要求", "value": position_info.language})

        return require
