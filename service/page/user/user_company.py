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
from util.tool import temp_date_tool, ps_tool
from tests.dev_data.user_company_config import COMPANY_CONFIG
import conf.path as path


class UserCompanyPageService(PageService):

    @gen.coroutine
    def get_company_data(self, handler_params, company, user):
        """Develop Status: To be modify with real data.
        :param handler_params:
        :param company: 当前公司
        :return:
        """
        data = ObjectDict()

        conds = {'user_id': user.id, 'company_id': company.id}
        fllw_cmpy = yield self.user_company_follow_ds.get_fllw_cmpy(
                        conds=conds, fields=['id', 'company_id'])
        vst_cmpy = yield self.user_company_visit_req_ds.get_visit_cmpy(
                        conds=conds, fields=['id', 'company_id'])

        if company.id != user.company.id:
            teams = yield ps_tool.get_sub_company_teams(self, company.id)
        else:
            teams = yield self.hr_team_ds.get_team_list(
                conds={'company_id': company.id})
        team_resource_list = yield self.get_team_resource(teams)
        team_template = temp_date_tool.make_company_team(
            team_resource_list, make_url(path.COMPANY_TEAM, handler_params))

        data.header = temp_date_tool.make_header(company)
        data.relation = ObjectDict({
            'follow': self.constant.YES if fllw_cmpy else self.constant.NO,
            'want_visit': self.constant.YES if vst_cmpy else self.constant.NO})
        data.templates = yield self._get_company_template(company.id)
        data.templates.insert(2, team_template)  # 暂且固定团队信息在公司主页位置
        data.template_total = len(data.templates)

        raise gen.Return(data)

    @gen.coroutine
    def _get_company_template(self, company_id):
        company_config = COMPANY_CONFIG.get(str(company_id))
        values = sum(company_config.config.values(), [])
        media_list = yield self.hr_media_ds.get_media_list(
            conds='id in {}'.format(tuple(values)))
        media = {str(m.id): m for m in media_list}

        templates = [
            getattr(temp_date_tool, 'make_company_{}'.format(key))(
                [media.get(str(id)) for id in company_config.config.get(key)]
            ) for key in company_config.order
        ]

        raise gen.Return(templates)

    @gen.coroutine
    def get_team_resource(self, team_list):
        media_dict = yield ps_tool.get_media_by_ids(
            [t.media_id for t in team_list])

        raise gen.Return([ObjectDict({
            # 'show_order': team.show_order, 如果需要对team排序
            'id': team.id,
            'title': team.name,
            'longtext': team.description,
            'media_url': media_dict.get(team.id).media_url,
            'media_type': media_dict.get(team.id).media_type,
        }) for team in team_list])

    @gen.coroutine
    def set_company_follow(self, param):
        """
        Store follow company.
        :param param: dict include target user company ids.
        :return:
        """
        user_id, company_id = param.get('user_id'), param.get('company_id'),
        status, source = param.get('status'), param.get('source', 0)

        conds = {'user_id': [user_id, '='], 'company_id': [company_id, '=']}
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
    def set_visit_company(self, param):
        """
        Store visiting company.
        :param param: dict include target user company ids.
        :return:
        """
        user_id, company_id = param.get('user_id'), param.get('company_id'),
        status, source = param.get('status'), param.get('source', 0)

        if int(status) == 0:
            raise gen.Return(False)

        conds = {'user_id': [user_id, '='], 'company_id': [company_id, '=']}
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


if __name__ == '__main__':
    print(getattr(temp_date_tool, 'make_company_working_env')())


    # temp_date_tool
    print('a')
