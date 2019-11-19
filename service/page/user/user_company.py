# coding=utf-8

import re
import operator

from urllib.parse import quote

from tornado import gen

import conf.path as path
from setting import settings
from service.page.base import PageService
from util.common import ObjectDict
from util.tool.url_tool import make_url, make_static_url
from util.tool import temp_data_tool
from util.tool import iterable_tool
from util.tool.temp_data_tool import make_up_for_missing_res
from tests.dev_data.user_company_config import COMPANY_CONFIG


class UserCompanyPageService(PageService):
    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_company_data(self, locale, handler_params, company, user):
        """
        构造企业主页，供企业号，gamma 使用
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

        # 拼装模板数据
        data.header = temp_data_tool.make_header(locale, company)

        # 实时检查用户对于公众号的关注情况
        follow = self.constant.NO
        check_follow_ret = yield self.user_wx_user_ds.get_wxuser(
            conds={'id': user.wxuser.id}, fields=['is_subscribe'])
        if check_follow_ret and check_follow_ret.is_subscribe:
            follow = self.constant.YES
        # 检查关注情况结束

        data.relation = ObjectDict({
            'want_visit': self.constant.YES if vst_cmpy else self.constant.NO,
            'qrcode': self._make_qrcode(user.wechat),
            'follow': follow
        })

        # 玛氏定制需求
        company_config = COMPANY_CONFIG.get(company.id)
        if company_config and company_config.get('custom_visit_recipe', False):
            data.relation.custom_visit_recipe = company_config.custom_visit_recipe
        else:
            data.relation.custom_visit_recipe = []

        data.templates = yield self._get_company_cms_page(company.id, user, team_index_url)
        data.template_total = len(data.templates)

        # 自定义团队文案
        teamname_custom = user.company.conf_teamname_custom

        # 如果是中文，使用中文"团队"，或者使用用户自定义的团队名称。
        if locale.code == 'zh_CN':
            teamname_custom.update(
                teamname_custom=locale.translate(
                    teamname_custom.teamname_custom,
                    plural_message=teamname_custom.teamname_custom,
                    count=2
                )
            )
        # 如果是英文， 默认使用 "Teams"
        elif locale.code == 'en_US':
            teamname_custom.update(
                teamname_custom=locale.translate(
                    '团队',
                    plural_message='团队',
                    count=2
                )
            )
        else:
            assert False  # should not be here as we just support 2 above locales

        data.bottombar = teamname_custom

        raise gen.Return(data)

    def _make_qrcode(self, wechat):
        multi_domain_settings = settings["multi_domain"]
        link_head = "https://" + multi_domain_settings["m_format"].format(wechat.appid) + '/image?url={}&wechat_signature='+wechat.signature
        if wechat.qrcode and not re.match(r'^http', wechat.qrcode):
            return quote(make_static_url(wechat.qrcode))
        elif wechat.qrcode and \
            not re.match(
                r'^https://platform.moseeker.com/recruit/image?url=', wechat.qrcode):
            return link_head.format(quote(make_static_url(wechat.qrcode)))
        return wechat.qrcode

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
                    conds="module_id in {} and disable=0 order by orders, id".format(tuple(cms_modules_ids)).replace(',)', ')')
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
                        "media_url": self._make_qrcode(user.wechat)
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
