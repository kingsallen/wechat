# coding=utf-8

from tornado import gen
import ujson

import conf.common as const
import conf.path as path
from handler.base import BaseHandler
from tests.dev_data.user_company_config import COMPANY_CONFIG
from util.common import ObjectDict
from util.common.decorator import check_sub_company, handle_response, \
    authenticated, NewJDStatusCheckerAddFlag
from util.tool.str_tool import add_item
import conf.path as path


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

    @handle_response
    @NewJDStatusCheckerAddFlag()
    @check_sub_company
    @gen.coroutine
    def get(self):
        company = self.params.pop('sub_company') if self.params.sub_company \
            else self.current_user.company
        # 判断来源
        if self.params.source == const.FANS_RECOMMEND:
            origin = const.SA_ORIGIN_FANS_RECOMMEND
        else:
            origin = const.SA_ORIGIN_PLATFORM
        self.track("cCompanyIndex", properties=ObjectDict(origin=origin))
        if self.flag_should_display_newjd:
            data = yield self.user_company_ps.get_company_data(
                self.locale, self.params, company, self.current_user)

            self.params.share = self._share(company)
            self.render_page(template_name='company/profile.html', data=data)
        else:
            company_data = ObjectDict()
            company = ObjectDict({
                "abbreviation": company.abbreviation,
                "name": company.name,
                "logo": self.static_url(company.logo),
                "industry": company.industry,
                "scale_name": company.scale_name,
                "homepage": company.homepage,
                "introduction": company.introduction,
                "impression": company.impression_processed
            })

            add_item(company_data, "company", company)
            self.render_page(
                template_name='company/info_old.html',
                data=company_data,
                meta_title=const.PAGE_COMPANY_INFO)

    def _share(self, company):
        company_name = company.abbreviation or company.name
        default = ObjectDict({
            'cover': self.share_url(company.get('logo')),
            'title': '关于{}, 你想知道的都在这里'.format(company_name),
            'description': '这可能是你人生的下一站! 看清企业全局, 然后定位自己',
            'link': self.make_url(
                    path.WECHAT_COMPANY,
                    self.params,
                    recom=self.position_ps._make_recom(self.current_user.sysuser.id))
        })
        # 玛氏定制
        config = COMPANY_CONFIG.get(company.id)
        if config and config.get('transfer', False) and config.transfer.get('cm', False):
            default.description = config.transfer.get('cm')

        return default


class CompanyInfoRedirectHandler(BaseHandler):
    """公司详情页老样式"""

    @handle_response
    @gen.coroutine
    def get(self, did):
        params = self.params
        did = int(did)
        current_company_id = self.current_user.company.id
        if did != current_company_id:
            # did不是当前公司, 那么只给看子公司
            maybe_sub_company = yield self.team_ps.get_sub_company(did)
            if maybe_sub_company and maybe_sub_company.parent_id == current_company_id:
                # 是子公司
                params.update({"did": str(did)})
            else:
                # 不是子公司 或 公司不存在, 不给看
                self.write_error(404)
                return
        else:
            # 正常访问本公司信息
            pass
        self.redirect_to_route("new_company_info_page", params)


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


class CompanyHrInfoHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):
        """获取hr信息"""
        hr_info = yield self.company_ps.get_main_hr_info(self.current_user.company.id)
        self.send_json_success(data=hr_info)


class NearbyStoresHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):
        """获取附近店铺"""
        if self.params.longitude and self.params.latitude:
            radius = self.params.radius

            params = ObjectDict({
                "company_id": self.current_user.company.id,
                "longitude": self.params.longitude,
                "latitude": self.params.latitude,
                "radius": int(radius) / 1000 if radius and int(radius) else 1
            })
        else:
            params = ObjectDict({
                "company_id": self.current_user.company.id
            })
            # ret = yield self.company_ps.get_lbs_ip_location(self.request.remote_ip)
            # longitude = ret.split(";")[0].split(",")[0]
            # latitude = ret.split(";")[0].split(",")[1]

        stores_info = yield self.company_ps.get_nearby_stores(params)

        if stores_info.data and stores_info.data.stores:
            for store in stores_info.data.stores:
                store.update({"coordinates": {"latitude": store["latitude"], "longitude": store["longitude"]}})
        self.send_json_success(data=stores_info.data)


class PositionLbsHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self, position_id):
        """根据职位id获取职位的LBS信息"""
        if self.params.longitude and self.params.latitude:
            radius = self.params.radius
            params = ObjectDict({
                "company_id": self.current_user.company.id,
                "longitude": self.params.longitude,
                "latitude": self.params.latitude,
                "radius": int(radius) / 1000 if radius and int(radius) else 1
            })
        else:
            params = ObjectDict({
                "company_id": self.current_user.company.id
            })
        #     ret = yield self.company_ps.get_lbs_ip_location(self.request.remote_ip)
        #     longitude = ret.split(";")[0].split(",")[0]
        #     latitude = ret.split(";")[0].split(",")[1]

        stores_info = yield self.company_ps.get_position_lbs_info(params, position_id)

        if stores_info.data and stores_info.data.stores:
            for store in stores_info.data.stores:
                store.update({"coordinates": {"latitude": store["latitude"], "longitude": store["longitude"]}})
        self.send_json_success(data=stores_info.data)
