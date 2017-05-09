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

        if company_info.conf_newjd_status != 2:
            # 老 JD 样式

        else:

            # 构造公司企业新主页
            data = yield self.user_company_ps.get_company_data(
                self.params, company_info, self.current_user)
            data.templates.append(hot_positions)
            self.send_json_success(data={
                "company": company,
                "templates": data.templates,
                "share": share,
                "cover": data.header.banner
            })

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

