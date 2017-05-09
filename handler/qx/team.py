# coding=utf-8

from tornado import gen

import conf.path as path
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response
from util.tool.url_tool import url_append_query


class TeamDetailHandler(BaseHandler):
    """Gamma 团队主页"""

    @handle_response
    @gen.coroutine
    def get(self, team_id):

        team = yield self.team_ps.get_team_by_id(int(team_id))
        if not team:
            self.write_error(404)
            return

        current_company = yield self.company_ps.get_company(conds={"id": team.company_id}, need_conf=True)

        data = yield self.team_ps.get_team_detail(
            self.current_user, current_company, team, self.params)

        share_cover_url = data.templates[0].data[0].get('media_url') or \
                          self.static_url(self.current_user.company.logo)

        share = self._share(team_id, current_company, team.name, share_cover_url)

        self.send_json_success(data={
            "team": data.templates,
            "share": share
        })

    def _share(self, team_id, company, team_name, share_cover_url):
        company_name = company.abbreviation or company.name
        default = ObjectDict({
            "cover": url_append_query(share_cover_url, "imageMogr2/thumbnail/!300x300r"),
            "title": "【{}】-{}的团队介绍".format(team_name, company_name),
            "description": '微信好友{}推荐，点击查看团队介绍。打开有职位列表哦！'.format(self.current_user.qxuser.nickname),
            "link": self.make_url(path.GAMMA_POSITION_TEAM.format(team_id),
                                  recom=self.position_ps._make_recom(self.current_user.sysuser.id),
                                  fr="recruit",
                                  did=str(company.id))
        })

        return default
