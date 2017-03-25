# -*- coding=utf-8 -*-
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
from util.tool.temp_data_tool import make_up_for_missing_res
from tests.dev_data.user_company_config import COMPANY_CONFIG
import conf.path as path
import re


class UserCompanyPageService(PageService):
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
        conds = {'user_id': user.sysuser.id, 'company_id': company.id}
        wx_user = yield self.user_wx_user_ds.get_wxuser(
            conds={'openid': user.wxuser.openid,
                   'wechat_id': user.wxuser.wechat_id},
            fields=['id', 'is_subscribe'])
        vst_cmpy = yield self.user_company_visit_req_ds.get_visit_cmpy(
            conds=conds, fields=['id', 'company_id'])
        team_index_url = make_url(path.COMPANY_TEAM, handler_params)

        # 拼装模板数据
        data.header = temp_data_tool.make_header(company)
        data.relation = ObjectDict({
            'want_visit': self.constant.YES if vst_cmpy else self.constant.NO,
            'qrcode': self._make_qrcode(user.wechat.qrcode),
            'follow': self.constant.YES if wx_user.is_subscribe
            else self.constant.NO,
        })
        company_config = COMPANY_CONFIG.get(company.id)
        if company_config and company_config.get('custom_visit_recipe', False):
            data.relation.custom_visit_recipe = company_config.custom_visit_recipe
        data.templates, tmp_team = yield self._get_company_template(
            company.id, team_index_url)

        # 如果没有提供team的配置，去hr_team寻找资源
        if not tmp_team:
            team_order = company_config.order.index('team')
            # 区分母公司、子公司对待，获取所有团队team
            if company.id != user.company.id:
                teams = yield self._get_sub_company_teams(company.id)
            else:
                teams = yield self.hr_team_ds.get_team_list(
                    conds={'company_id': company.id, 'is_show': 1, 'disable': 0})

            if teams:
                teams.sort(key=lambda t: t.show_order)
                teams = teams[0:6]  # 企业主业团队数不超过6个
                team_resource_list = yield self._get_team_resource(teams)
                team_template = temp_data_tool.make_company_team(
                    team_resource_list, team_index_url)
                data.templates.insert(team_order, team_template)

        data.template_total = len(data.templates)

        teamname_custom = yield self.hr_company_conf_ds.get_company_teamname_custom(user.company.id)
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
    def _get_company_template(self, company_id, team_index_url):
        """
        根据不同company_id去配置文件中获取company配置信息
        之后根据配置，生成template数据
        :param company_id:
        :return:
        """
        company_config = COMPANY_CONFIG.get(company_id)
        values = sum(company_config.config.values(), [])
        media_dict = yield self.hr_media_ds.get_media_by_ids(values)
        resources_dict = yield self.hr_resource_ds.get_resource_by_ids(
            [m.res_id for m in media_dict.values()])

        for m in media_dict.values():
            res = resources_dict.get(m.res_id, False)
            m.media_url = res.res_url if res else ''
            m.media_type = res.res_type if res else 0

        if company_config.config.get('team'):
            for team_media_id in company_config.config.get('team'):
                media_dict.get(team_media_id).link = team_index_url

        templates = [
            getattr(temp_data_tool, 'make_company_{}'.format(key))(
                [media_dict.get(mid) for mid in company_config.config.get(key)]
            ) for key in company_config.order
            if isinstance(company_config.config.get(key), list)
            ]

        raise gen.Return((templates, bool(company_config.config.get('team'))))

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
