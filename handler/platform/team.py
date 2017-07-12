# coding=utf-8
# Copyright 2016 MoSeeker


from tornado import gen

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
            current_company, self.params, sub_company_flag, self.current_user.company)

        self.params.share = self._share(current_company)

        self.render_page('company/team.html', data, meta_title=data.bottombar.teamname_custom)


    def _share(self, company):
        company_name = company.abbreviation or company.name
        default = ObjectDict({
            "cover": self.static_url(company.logo),
            "title": company_name + "的核心团队点此查看",
            "description": "这可能是你人生的下一站! 不先了解一下未来同事吗?",
            "link": self.fullurl()
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

        # 校验 pid
        pid = self.params.pid
        if not pid.isdigit() or not pid:
            self.write_error(404)
            raise gen.Return()

        current_company = self.params.pop('sub_company') if \
            self.params.sub_company else self.current_user.company

        team = yield self.team_ps.get_team_by_id(team_id)

        # 如果查不到 Team 或者
        # 查到 team 但是该 Team 不属于当前公司，
        # 跳转到 team 不存在页面
        if team.company_id != self.current_user.company.id:
            teamname = self.current_user.company.conf_teamname_custom.\
                teamname_custom
            data = {
                "pid": int(pid),
                "teamName": teamname
            }
            self.render_page(template_name='company/team_404.html', data=data)
            return

        data = yield self.team_ps.get_team_detail(
            self.current_user, current_company, team, self.params)

        share_cover_url = data.templates[0].data[0].get('media_url') or \
                          self.static_url(self.current_user.company.logo)
        self.params.share = self._share(current_company,
                                        team.name, share_cover_url)
        self.render_page(template_name='company/team.html', data=data,
                         meta_title=data.bottombar.teamname_custom)

    def _share(self, company, team_name, share_cover_url):
        company_name = company.abbreviation or company.name
        default = ObjectDict({
            "cover": url_append_query(share_cover_url, "imageMogr2/thumbnail/!300x300r"),
            "title": team_name.upper() + "-" + company_name,
            "description": '通常你在点击“加入我们”之类的按钮之前并不了解我们, 现在给你个机会!',
            "link": self.fullurl()
        })
        config = COMPANY_CONFIG.get(company.id)
        if config and config.get('transfer', False) and config.transfer.get('td', False):
            default.description = config.transfer.get('td')

        return default
