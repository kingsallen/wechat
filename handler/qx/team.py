# coding=utf-8
# Copyright 2016 MoSeeker


from tornado import gen

from handler.base import BaseHandler
from tests.dev_data.user_company_config import COMPANY_CONFIG
from util.common import ObjectDict
from util.common.decorator import NewJDStatusChecker404, check_sub_company, \
    handle_response
from util.tool.url_tool import url_append_query


class TeamDetailHandler(BaseHandler):

    @NewJDStatusChecker404()
    @handle_response
    @gen.coroutine
    def get(self, team_id):

        team = yield self.team_ps.get_team_by_id(team_id)
        current_company = yield self.company_ps.get_company(conds={"id": team.company_id}, need_conf=True)

        if team.company_id != self.current_user.company.id:
            self.write_error(404)
            raise gen.Return()

        data = yield self.team_ps.get_team_detail(
            self.current_user, current_company, team, self.params)

        share_cover_url = data.templates[0].data[0].get('media_url') or \
                          self.static_url(self.current_user.company.logo)
        share = self._share(current_company, team.name, share_cover_url)

        self.send_json_success(data={
            "team": data.templates,
            "share": share
        })

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
