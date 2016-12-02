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
        """

        :param handler_params:
        :param company: 当前公司
        :return:
        """
        data = ObjectDict()
        self.logger.debug('ps user: {}'.format(user))

        # 获取当前公司关注，访问信息
        conds = {'user_id': user.sysuser.id, 'company_id': company.id}
        fllw_cmpy = yield self.user_company_follow_ds.get_fllw_cmpy(
                        conds=conds, fields=['id', 'company_id'])
        vst_cmpy = yield self.user_company_visit_req_ds.get_visit_cmpy(
                        conds=conds, fields=['id', 'company_id'])

        # 区分母公司，子公司对待，获取所有团队team
        if company.id != user.company.id:
            teams = yield ps_tool.get_sub_company_teams(self, company.id)
        else:
            teams = yield self.hr_team_ds.get_team_list(
                conds={'company_id': company.id})
        team_resource_list = yield self.get_team_resource(teams)
        team_template = temp_date_tool.make_company_team(
            team_resource_list, make_url(path.COMPANY_TEAM, handler_params))

        # 拼装模板数据
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
        """
        根据不同company_id去配置文件中获取company配置信息
        之后根据配置，生成template数据
        :param company_id:
        :return:
        """
        company_config = COMPANY_CONFIG.get(str(company_id))
        values = sum(company_config.config.values(), [])
        media = yield ps_tool.get_media_by_ids(self, tuple(values))

        templates = [
            getattr(temp_date_tool, 'make_company_{}'.format(key))(
                [media.get(id) for id in company_config.config.get(key)]
            ) for key in company_config.order
            if company_config.config.get(key) or key == 'survey'
        ]

        raise gen.Return(templates)

    @gen.coroutine
    def get_team_resource(self, team_list):
        media_dict = yield ps_tool.get_media_by_ids(
            self, [t.media_id for t in team_list])

        raise gen.Return([ObjectDict({
            # 'show_order': team.show_order, 如果需要对team排序
            'id': team.id,
            'title': team.name,
            'longtext': team.description,
            'media_url': media_dict.get(team.media_id).media_url,
            'media_type': media_dict.get(team.media_id).media_type,
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
