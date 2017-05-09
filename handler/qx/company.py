# coding=utf-8

from tornado import gen

import conf.path as path
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response

class CompanyHandler(BaseHandler):
    """Gamma公司详情页新样式"""

    @handle_response
    @gen.coroutine
    def get(self, did):

        company_info = yield self.company_ps.get_company(
            conds={"id": int(did)}, need_conf=True)

        if not company_info:
            return self.write_error(404)

        if self.params.page_no > 1:
            # 热招职位翻页
            ret = yield self._make_position_list(did, self.params.page_no)
            self.send_json_success(data=ObjectDict(
                result=ret
            ))
            return

        # 构造企业热招企业列表
        hot_positions = yield self._make_position_list_template(did)

        share = self._share(company_info)
        company = ObjectDict(
            id=company_info.id,
            logo=self.static_url(company_info.logo),
            name=company_info.name,
            abbreviation=company_info.abbreviation,
            description=company_info.introduction,
        )

        data = ObjectDict(
            company=company,
            share=share,
        )

        templates = list()
        if company_info.conf_newjd_status != 2:
            # 老 JD 样式
            cover = company_info.banner
            intro_tem = self._make_intro_template(company_info)
            basic_tem = self._make_basicinfo_template(company_info)
            templates.append(intro_tem)
            templates.append(basic_tem)
            templates.append(hot_positions)
        else:
            # 构造公司企业新主页
            data = yield self.user_company_ps.get_company_data(
                self.params, company_info, self.current_user)
            templates = data.templates
            templates.append(hot_positions)
            cover = data.header.banner

        data.update({
            "cover": cover,
            "templates": templates
        })
        self.send_json_success(data=data)

    def _share(self, company):

        company_name = company.abbreviation or company.name
        default = ObjectDict({
            'cover': self.static_url(company.logo),
            'title': '{}的公司介绍'.format(company_name),
            'description': '微信好友{}推荐，点击查看公司介绍。打开有公司职位列表哦！'.format(self.current_user.qxuser.nickname),
            'link': self.make_url(path.GAMMA_POSITION_COMPANY.format(company.id), fr="recruit", did=str(company.id))
        })

        return default

    @gen.coroutine
    def _make_position_list(self, company_id, page_no):
        """
        热招职位分页
        :param company_id:
        :param page_no:
        :param page_size:
        :return:
        """
        ret = yield self.company_ps.get_company_positions(company_id, page_no)
        return ret

    @gen.coroutine
    def _make_position_list_template(self, company_id):
        """
        构造该企业热招职位，拼装 templates
        :param company_id:
        :return:
        """

        ret = yield self.company_ps.get_company_positions(company_id)
        default = ObjectDict(
            type=6,
            title="该企业热招职位",
            data=ret
        )
        return default

    def _make_intro_template(self, company_info):
        """
        构造企业介绍，拼装 templates
        :param company_id:
        :return:
        """

        default = ObjectDict(
            type=7,
            title="企业介绍",
            data= list(company_info.introduction)
        )
        return default

    def _make_basicinfo_template(self, company_info):
        """
        构造企业基本信息，拼装 templates
        :param company_id:
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
                "value": "{}人".format(company_info.scale),
            })
        if company_info.homepage:
            data.append({
                "name": "官网地址",
                "value": company_info.homepage,
            })

        default = ObjectDict(
            type=7,
            title="企业介绍",
            data=data
        )
        return default
