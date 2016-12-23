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
from tests.dev_data.user_company_config import COMPANY_CONFIG
import conf.path as path


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
        fllw_cmpy = yield self.user_company_follow_ds.get_fllw_cmpy(
                        conds=conds, fields=['id', 'company_id'])
        vst_cmpy = yield self.user_company_visit_req_ds.get_visit_cmpy(
                        conds=conds, fields=['id', 'company_id'])
        team_index_url = make_url(path.COMPANY_TEAM, handler_params)

        # 拼装模板数据
        data.header = temp_data_tool.make_header(company)
        data.relation = ObjectDict({
            'follow': self.constant.YES if fllw_cmpy else self.constant.NO,
            'want_visit': self.constant.YES if vst_cmpy else self.constant.NO
        })
        if COMPANY_CONFIG.get(company.id).get('custom_visit_recipe', False):
            data.relation.custom_visit_recipe = COMPANY_CONFIG.get(
                company.id).custom_visit_recipe
        data.templates, tmp_team = yield self._get_company_template(
            company.id, team_index_url)

        # 如果没有提供team的配置，去hr_team寻找资源
        if not tmp_team:
            team_order = COMPANY_CONFIG.get(company.id).order.index('team')
            # 区分母公司、子公司对待，获取所有团队team
            if company.id != user.company.id:
                teams = yield self._get_sub_company_teams(company.id)
            else:
                teams = yield self.hr_team_ds.get_team_list(
                    conds={'company_id': company.id, 'is_show': 1})
            teams.sort(key=lambda t: t.show_order)
            team_resource_list = yield self._get_team_resource(teams)
            team_template = temp_data_tool.make_company_team(
                team_resource_list, team_index_url)
            data.templates.insert(team_order, team_template)

        data.template_total = len(data.templates)

        raise gen.Return(data)

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
        media = yield self.hr_media_ds.get_media_by_ids(values)
        resources_dict = yield self.hr_resource_ds.get_resource_by_ids(
            [m.res_id for m in media])

        for m in media:
            res = resources_dict.get(m.res_id, False)
            if res:
                m.media_url = res.res_url
                m.media_type = res.res_type

        if company_config.config.get('team'):
            for team_media_id in company_config.config.get('team'):
                media.get(team_media_id).link = team_index_url

        templates = [
            getattr(temp_data_tool, 'make_company_{}'.format(key))(
                [media.get(mid) for mid in company_config.config.get(key)]
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
            conds='id in {} and is_show=1'.format(
                team_id_tuple).replace(',)', ')'))

        raise gen.Return(teams)

    @gen.coroutine
    def _get_team_resource(self, team_list):
        resource_dict = yield self.hr_resource_ds.get_resource_by_ids(
            [t.res_id for t in team_list])

        raise gen.Return([ObjectDict({
            'id': team.id,
            'title': '我们的团队',
            'subtitle': team.name,
            'longtext': team.summary,
            'media_url': resource_dict.get(team.res_id).res_url,
            'media_type': resource_dict.get(team.res_id).res_type,
        }) for team in team_list])

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
