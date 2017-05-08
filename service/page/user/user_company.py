# coding=utf-8
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.11

"""

from tornado import gen

from service.page.base import PageService
from util.common import ObjectDict
from util.tool.url_tool import make_url
from util.tool import temp_data_tool
from util.tool import iterable_tool
from util.tool.temp_data_tool import make_up_for_missing_res
from tests.dev_data.user_company_config import COMPANY_CONFIG
import conf.path as path
import re
import operator


class UserCompanyPageService(PageService):
    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_company_data(self, handler_params, company, user):
        """

        :param handler_params:
        :param company: 当前公司
        :param user: current_user
        :return:
        """
        data = ObjectDict()

        # 获取当前公司关注，访问信息
        vst_cmpy = False
        if user.sysuser.id:
            conds = {'user_id': user.sysuser.id, 'company_id': company.id}
            vst_cmpy = yield self.user_company_visit_req_ds.get_visit_cmpy(
                conds=conds, fields=['id', 'company_id'])
        team_index_url = make_url(path.COMPANY_TEAM, handler_params, self.settings.platform_host)

        self.logger.debug("get_company_data:{}".format(team_index_url))

        # 拼装模板数据
        data.header = temp_data_tool.make_header(company)
        data.relation = ObjectDict({
            'want_visit': self.constant.YES if vst_cmpy else self.constant.NO,
            'qrcode': self._make_qrcode(user.wechat.qrcode),
            'follow': self.constant.YES if user.wxuser.is_subscribe
            else self.constant.NO,
        })

        # 玛氏定制需求
        company_config = COMPANY_CONFIG.get(company.id)
        if company_config and company_config.get('custom_visit_recipe', False):
            data.relation.custom_visit_recipe = company_config.custom_visit_recipe
        else:
            data.relation.custom_visit_recipe = []

        data.templates = yield self._get_company_cms_page(company.id, user, team_index_url)

        self.logger.debug("get_company_data templates:{}".format(data.templates))

        data.template_total = len(data.templates)

        # 自定义团队文案
        teamname_custom = user.company.conf_teamname_custom
        data.bottombar = teamname_custom

        raise gen.Return(data)

    @staticmethod
    def _make_qrcode(qrcode_url):
        link_head = 'https://www.moseeker.com/common/image?url={}'
        if qrcode_url and \
            not re.match(
                r'^https://www.moseeker.com/common/image?url=',
                qrcode_url):
            return link_head.format(qrcode_url)
        return qrcode_url

    @gen.coroutine
    def _get_company_cms_page(self, company_id, user, team_index_url):
        """
        [hr3.4]不在从配置文件中去获取企业首页豆腐块配置信息, 而是从hr_cms_*系列数据库获取数据
        :param company_id:
        :return:
        """
        templates = []
        cms_page = yield self.hr_cms_pages_ds.get_page(conds={
            "config_id": company_id,
            "type": self.constant.CMS_PAGES_TYPE_COMPANY_INDEX,
            "disable": 0
        })
        if cms_page:
            cms_page_id = cms_page.id
            cms_modules = yield self.hr_cms_module_ds.get_module_list(conds={
                "page_id": cms_page_id,
                "disable": 0
            })
            if cms_modules:
                cms_modules.sort(key=operator.itemgetter("orders"))  # 模块排序

                cms_modules_ids = [m.id for m in cms_modules]
                cms_medias = yield self.hr_cms_media_ds.get_media_list(
                    conds="module_id in {} and disable=0".format(tuple(cms_modules_ids)).replace(',)', ')')
                )

                # 不需要价差cms_medias存不存在
                cms_medias_res_ids = [m.res_id for m in cms_medias]
                resources_dict = yield self.hr_resource_ds.get_resource_by_ids(cms_medias_res_ids)
                for m in cms_medias:
                    res = resources_dict.get(m.res_id, False)
                    m.media_url = res.res_url if res else ''
                    m.media_type = res.res_type if res else 0

                # 给二维码模块注入qrcode地址
                qrcode_module = list(
                    filter(lambda m: m.get("type") == self.constant.CMS_PAGES_MODULE_QRCODE, cms_modules))
                if len(qrcode_module) > 0:
                    qrcode_module = qrcode_module[0]
                    qrcode_module_id = qrcode_module.id
                    qrcode_cms_media = ObjectDict({
                        "module_id": qrcode_module_id,
                        "media_type": self.constant.CMS_PAGES_RESOURCES_TYPE_IMAGE,
                        "company_name": user.wechat.name,
                        "media_url": self._make_qrcode(user.wechat.qrcode)
                    })
                    cms_medias.append(qrcode_cms_media)

                cms_medias = iterable_tool.group(cms_medias, "module_id")
                templates = [getattr(temp_data_tool, "make_company_module_type_{}".format(module.type))(
                    cms_medias.get(module.id, []), module.module_name, module.link)
                             for module in cms_modules]
        return templates

    @gen.coroutine
    def _get_sub_company_teams(self, company_id):
        """
        获取团队信息
        当只给定company_id，通过position信息中team_id寻找出所有相关团队
        :param self:
        :param company_id:
        :return: [object_of_hr_team, ...]
        """
        publishers = yield self.hr_company_account_ds.get_company_accounts_list(
            conds={'company_id': company_id}, fields=None)
        publisher_id_tuple = tuple([p.account_id for p in publishers])

        if not publisher_id_tuple:
            raise gen.Return([])
        team_ids = yield self.job_position_ds.get_positions_list(
            conds='publisher in {}'.format(
                publisher_id_tuple).replace(',)', ')'),
            fields=['team_id'], options=['DISTINCT'])
        team_id_tuple = tuple([t.team_id for t in team_ids])

        if not team_id_tuple:
            gen.Return([])
        teams = yield self.hr_team_ds.get_team_list(
            conds='id in {} and is_show=1 and disable=0'.format(
                team_id_tuple).replace(',)', ')'))

        raise gen.Return(teams)

    @gen.coroutine
    def _get_team_resource(self, team_list):
        resource_dict = yield self.hr_resource_ds.get_resource_by_ids(
            [t.res_id for t in team_list])

        team_resource = []
        for team in team_list:
            team_res = make_up_for_missing_res(resource_dict.get(team.res_id))
            team_resource.append(ObjectDict({
                'id': team.id,
                'title': '我们的团队',
                'sub_title': team.name,
                'longtext': team.summary,
                'media_url': team_res.res_url,
                'media_type': team_res.res_type,
            }))

        raise gen.Return(team_resource)

    @gen.coroutine
    def set_company_follow(self, current_user, param):
        """
        Store follow company.
        :param param: dict include target user company ids.
        :return:
        """
        user_id = current_user.sysuser.id
        status, source = param.get('status'), param.get('source', 0)
        current_user.company.id
        # 区分母公司子公司对待
        company_id = param.sub_company.id if param.did \
                                             and param.did != current_user.company.id else current_user.company.id

        conds = {'user_id': user_id, 'company_id': company_id}
        company = yield self.user_company_follow_ds.get_fllw_cmpy(
            conds=conds, fields=['id', 'user_id', 'company_id'])

        if company:
            response = yield self.user_company_follow_ds.update_fllw_cmpy(
                conds=conds,
                fields={'status': status, 'source': source})
        else:
            response = yield self.user_company_follow_ds.create_fllw_cmpy(
                fields={'user_id': user_id, 'company_id': company_id,
                        'status': status, 'source': source})
        result = True if response else False

        raise gen.Return(result)

    @gen.coroutine
    def set_visit_company(self, current_user, param):
        """
        Store visiting company.
        :param current_user: self.current_user in handler
        :param param: self.params in handler
        :return:
        """

        user_id = current_user.sysuser.id
        status, source = param.get('status'), param.get('source', 0)

        if not user_id:
            raise gen.Return(False)

        # 区分母公司子公司对待
        company_id = param.sub_company.id if param.did \
                                             and param.did != current_user.company.id else current_user.company.id

        if int(status) == 0:
            raise gen.Return(False)

        conds = {'user_id': user_id, 'company_id': company_id}
        company = yield self.user_company_visit_req_ds.get_visit_cmpy(
            conds, fields=['id', 'user_id', 'company_id'])

        if company:
            response = yield self.user_company_visit_req_ds.update_visit_cmpy(
                conds=conds,
                fields={'status': status, 'source': source})
        else:
            response = yield self.user_company_visit_req_ds.create_visit_cmpy(
                fields={'user_id': user_id, 'company_id': company_id,
                        'status': status, 'source': source})

        result = True if response else False

        raise gen.Return(result)
