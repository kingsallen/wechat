# coding=utf-8
# Copyright 2016 MoSeeker

from tornado import gen

import conf.path as path
import conf.common as const
from handler.base import BaseHandler
from tests.dev_data.user_company_config import COMPANY_CONFIG
from util.common import ObjectDict
from util.common.decorator import NewJDStatusChecker404, check_sub_company, \
    handle_response
from util.tool.url_tool import url_append_query


class TeamIndexHandler(BaseHandler):

    @handle_response
    @NewJDStatusChecker404()
    @check_sub_company
    @gen.coroutine
    def get(self):

        if self.params.sub_company:
            sub_company_flag = True
            current_company = self.params.pop('sub_company')
        else:
            sub_company_flag = False
            current_company = self.current_user.company

        data = yield self.team_ps.get_team_index(
            self.locale, current_company, self.params, sub_company_flag, self.current_user.company)

        self.params.share = self._share(current_company)
        # 判断来源
        if self.params.source == const.FANS_RECOMMEND:
            origin = const.SA_ORIGIN_FANS_RECOMMEND
        else:
            origin = const.SA_ORIGIN_PLATFORM
        self.track("cTeamIndex", properties=ObjectDict(origin=origin))
        self.render_page('company/team.html', data, meta_title=data.bottombar.teamname_custom)

    def _share(self, company):
        company_name = company.abbreviation or company.name
        default = ObjectDict({
            "cover": self.share_url(company.logo),
            "title": company_name + "的核心团队点此查看",
            "description": "这可能是你人生的下一站! 不先了解一下未来同事吗?",
            'link': self.make_url(
                path.COMPANY_TEAM,
                self.params,
                recom=self.position_ps._make_recom(self.current_user.sysuser.id))
        })
        config = COMPANY_CONFIG.get(company.id)
        if config and config.get('transfer', False) and config.transfer.get('tl', False):
            default.description = config.transfer.get('tl')

        return default


class TeamDetailHandler(BaseHandler):

    @handle_response
    @NewJDStatusChecker404()
    @check_sub_company
    @gen.coroutine
    def get(self, team_id):

        current_company = self.params.pop('sub_company') if \
            self.params.sub_company else self.current_user.company

        team = yield self.team_ps.get_team_by_id(team_id)

        # 如果查不到 Team 或者
        # 查到 team 但是该 Team 不属于当前公司，
        # 跳转到 team 不存在页面
        if team.company_id != self.current_user.company.id:
            self.render_page(
                template_name='company/team_404.html',
                data={"teamName": self.current_user.company.conf_teamname_custom.teamname_custom})
            return

        data = yield self.team_ps.get_team_detail(
            self.locale, self.current_user, current_company, team, self.params)

        share_cover_url = data.templates[0].data[0].get('media_url') or \
                          self.static_url(self.current_user.company.logo)
        self.params.share = self._share(current_company, team.name, share_cover_url, team_id)

        # 判断来源
        if self.params.source == const.FANS_RECOMMEND:
            origin = "fans_recommend"
        else:
            origin = "platform"
        self.track("cTeamDetail", properties=ObjectDict(origin=origin))

        self.render_page(template_name='company/team.html', data=data,
                         meta_title=data.bottombar.teamname_custom)

    def _share(self, company, team_name, share_cover_url, team_id):
        company_name = company.abbreviation or company.name
        default = ObjectDict({
            "cover": self.share_url(url_append_query(share_cover_url, "imageMogr2/thumbnail/!300x300r")),
            "title": team_name.upper() + "-" + company_name,
            "description": '通常你在点击“加入我们”之类的按钮之前并不了解我们, 现在给你个机会!',
            'link': self.make_url(
                path.TEAM_PATH.format(team_id),
                self.params,
                recom = self.position_ps._make_recom(self.current_user.sysuser.id))})

        config = COMPANY_CONFIG.get(company.id)
        if config and config.get('transfer', False) and config.transfer.get('td', False):
            default.description = config.transfer.get('td')

        return default
