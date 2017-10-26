# coding=utf-8

from tornado import gen

import conf.path as path
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response
from conf.qx import JD_BACKGROUND_IMG
from util.tool.url_tool import make_static_url

class CompanyHandler(BaseHandler):
    """Gamma公司详情页新样式"""

    @handle_response
    @gen.coroutine
    def get(self, did):

        company_info = yield self.company_ps.get_company(
            conds={"id": int(did)}, need_conf=True)

        if not company_info:
            self.send_json_error()
            return

        main_hr_info = yield self.company_ps.get_main_hr_info(company_info.id)

        share = self._share(company_info)
        company = ObjectDict(
            id=company_info.id,
            hr_chat=bool(company_info.conf_hr_chat),
            logo=self.static_url(company_info.logo),
            name=company_info.name,
            abbreviation=company_info.abbreviation,
            description=company_info.introduction
        )

        data = ObjectDict(
            company=company,
            main_hr_info=main_hr_info,
            share=share,
        )

        templates = list()
        if company_info.conf_newjd_status != 2:
            # 老 JD 样式
            cover =  company_info.banner[0] if company_info.banner else ""
            intro_tem = self._make_intro_template(company_info)
            basic_tem = self._make_basicinfo_template(company_info)
            impression_tem = self._make_impression_template(company_info)
            team_tem = yield self._make_team_template(company_info)
            if intro_tem:
                templates.append(intro_tem)
            templates.append(basic_tem)
            if impression_tem:
                templates.append(impression_tem)
            if team_tem:
                templates.append(team_tem)
        else:
            # 构造公司企业新主页
            company_data = yield self.user_company_ps.get_company_data(
                self.locale, self.params, company_info, self.current_user)
            templates = company_data.templates
            cover = company_data.header.banner

        # hack if no cover is provided, try to get the default industry img
        if not cover:
            industry_name = company_info.industry
            industry_type = yield self.dictionary_ps.get_industry_type_by_name(industry_name)
            cover = JD_BACKGROUND_IMG.get(industry_type, {}).get('company_img')
            cover = make_static_url(cover)

        data.update({
            "cover": cover,
            "templates": templates
        })
        self.send_json_success(data=data)

    def _share(self, company):

        company_name = company.abbreviation or company.name
        default = ObjectDict({
            'cover': self.share_url(company.logo),
            'title': '{}的公司介绍'.format(company_name),
            'description': '微信好友{}推荐，点击查看公司介绍。打开有公司职位列表哦！'.format(self.current_user.qxuser.nickname),
            'link': self.make_url(path.GAMMA_POSITION_COMPANY.format(company.id),
                                  recom=self.position_ps._make_recom(self.current_user.sysuser.id),
                                  fr="recruit",
                                  did=str(company.id))
        })

        return default

    def _make_intro_template(self, company_info):
        """
        构造 老 JD企业介绍，拼装 templates
        :param company_info:
        :return:
        """

        if not company_info.introduction:
            return None

        default = ObjectDict(
            type=7,
            title="企业介绍",
            data= [company_info.introduction]
        )
        return default

    def _make_basicinfo_template(self, company_info):
        """
        构造老 JD企业基本信息，拼装 templates
        :param company_info:
        :return:
        """

        data = list()
        if company_info.name:
            data.append({
                "name": "公司全称",
                "value": company_info.name,
            })
        if company_info.industry:
            data.append({
                "name": "所属行业",
                "value": company_info.industry,
            })
        if company_info.scale:
            data.append({
                "name": "企业规模",
                "value": company_info.scale_name,
            })
        if company_info.homepage:
            data.append({
                "name": "官网地址",
                "value": company_info.homepage,
            })

        default = ObjectDict(
            type=8,
            title="基本信息",
            data=data
        )
        return default

    def _make_impression_template(self, company_info):
        """
        构造老 JD企业impression信息，拼装 templates
        :param company_info:
        :return:
        """
        if not company_info.impression:
            return None

        default = ObjectDict(
            type=10,
            title="公司环境",
            data=company_info.impression
        )
        return default

    @gen.coroutine
    def _make_team_template(self, company_info):
        """
        构造 老 JD 团队职位数，拼装 templates
        :param company_info:
        :return:
        """
        ret = yield self.team_ps.get_gamma_company_team(company_info.id)

        if not ret:
            return None

        default = ObjectDict(
            type=9,
            title="企业团队",
            data=ret
        )
        return default
