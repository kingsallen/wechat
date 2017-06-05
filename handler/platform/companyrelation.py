# coding=utf-8

"""
:author 马超（machao@moseeker.com）
:date 2016.10.11

"""
import ujson

from tornado import gen

import conf.common as const
from handler.base import BaseHandler
from tests.dev_data.user_company_config import COMPANY_CONFIG
from util.common import ObjectDict
from util.common.decorator import check_sub_company, handle_response, \
    authenticated
from util.tool.str_tool import add_item


class CompanyVisitReqHandler(BaseHandler):

    @handle_response
    @check_sub_company
    @authenticated
    @gen.coroutine
    def post(self):
        try:
            self.guarantee('status')
        except:
            raise gen.Return()

        result = yield self.user_company_ps.set_visit_company(
            current_user=self.current_user, param=self.params)

        if not result:
            self.send_json_error()
            return
        self.send_json_success()


class CompanyFollowHandler(BaseHandler):

    @handle_response
    @check_sub_company
    @authenticated
    @gen.coroutine
    def post(self):
        try:
            self.guarantee('status')
        except:
            raise gen.Return()

        result = yield self.user_company_ps.set_company_follow(
            current_user=self.current_user, param=self.params)

        if not result:
            self.send_json_error()
            return
        self.send_json_success()


class CompanyHandler(BaseHandler):
    """公司详情页新样式"""

    @handle_response
    @check_sub_company
    @gen.coroutine
    def get(self):
        company = self.params.pop('sub_company') if self.params.sub_company \
            else self.current_user.company

        data = yield self.user_company_ps.get_company_data(
            self.params, company, self.current_user)

        self.params.share = self._share(company)
        self.render_page(template_name='company/profile.html', data=data)

    def _share(self, company):
        company_name = company.abbreviation or company.name
        default = ObjectDict({
            'cover': self.static_url(company.get('logo', '')),
            'title': '关于{}, 你想知道的都在这里'.format(company_name),
            'description': '这可能是你人生的下一站! 看清企业全局, 然后定位自己',
            'link': self.fullurl()
        })
        # 玛氏定制
        config = COMPANY_CONFIG.get(company.id)
        if config and config.get('transfer', False) and config.transfer.get('cm', False):
            default.description = config.transfer.get('cm')

        return default


class CompanyInfoHandler(BaseHandler):
    """公司详情页老样式"""

    @handle_response
    @gen.coroutine
    def get(self, did):

        company_info = yield self.company_ps.get_company(
            conds={"id": did}, need_conf=True)

        company_data = ObjectDict()
        company = ObjectDict({
            "abbreviation": company_info.abbreviation,
            "name": company_info.name,
            "logo": self.static_url(company_info.logo),
            "industry": company_info.industry,
            "scale_name": company_info.scale_name,
            "homepage": company_info.homepage,
            "introduction": company_info.introduction,
            "impression": company_info.impression_processed
        })

        add_item(company_data, "company", company)
        self.render_page(
            template_name='company/info_old.html',
            data=company_data,
            meta_title=const.PAGE_COMPANY_INFO)


class CompanySurveyHandler(BaseHandler):
    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        """处理用户填写公司 survey 的 post api 请求"""
        try:
            self.guarantee('selected', 'other')
        except:
            raise gen.Return()

        _company_id = self.current_user.company.id
        _sysuser_id = self.current_user.sysuser.id
        _selected = ujson.dumps(self.params.selected, ensure_ascii=False)
        _other = self.params.other or ''

        inserted_id = yield self.company_ps.save_survey({
            'company_id': _company_id,
            'sysuser_id': _sysuser_id,
            'selected': _selected,
            'other': _other
        })

        if inserted_id and int(inserted_id):
            self.send_json_success()
        else:
            self.send_json_error()
