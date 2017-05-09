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
            self.send_json_error()
            return

        current_company = yield self.company_ps.get_company(conds={"id": team.company_id}, need_conf=True)

        self.logger.debug("Team team:{}".format(team))
        self.logger.debug("Team current_company:{}".format(current_company))

        data = yield self.team_ps.get_team_detail(
            self.current_user, current_company, team, self.params)

        share_cover_url = data.templates[0].data[0].get('media_url') or \
                          self.static_url(self.current_user.company.logo)
        share_cover = url_append_query(share_cover_url, "imageMogr2/thumbnail/!300x300r")

        share = self._share(team_id, current_company, team.name, share_cover_url)

        basic_team = self._make_team(team)

        self.send_json_success(data={
            "team": basic_team,
            "templates": data.templates,
            "share": share,
            "cover": share_cover
        })

    def _share(self, team_id, company, team_name, share_cover):

        company_name = company.abbreviation or company.name
        default = ObjectDict({
            "cover": share_cover,
            "title": "【{}】-{}的团队介绍".format(team_name, company_name),
            "description": '微信好友{}推荐，点击查看团队介绍。打开有职位列表哦！'.format(self.current_user.qxuser.nickname),
            "link": self.make_url(path.GAMMA_POSITION_TEAM.format(team_id),
                                  recom=self.position_ps._make_recom(self.current_user.sysuser.id),
                                  fr="recruit",
                                  did=str(company.id))
        })

        return default

    def _make_team(self, team):

        """
        构造团队信息
        :param team:
        :return:
        """

        default = ObjectDict(
            id=team.id,
            name=team.name,
            description=team.description,
        )

        return default
