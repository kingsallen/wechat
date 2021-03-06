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

        templates, share_cover = yield self._make_team_template(current_company, team)
        share = self._share(team_id, current_company, team.name, share_cover)
        basic_team = self._make_team(team, current_company)

        self.send_json_success(data={
            "team": basic_team,
            "templates": templates,
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
                                  self.params,
                                  recom=self.position_ps._make_recom(self.current_user.sysuser.id),
                                  fr="recruit",
                                  tid=str(team_id),
                                  did=str(company.id))
        })

        return default

    def _make_team(self, team, company):

        """
        构造团队信息
        :param team:
        :return:
        """

        default = ObjectDict(
            id=team.id,
            did=company.id,
            name=team.name,
            description=team.description,
        )

        return default

    @gen.coroutine
    def _make_team_template(self, current_company, team):

        data = yield self.team_ps.get_team_detail(
            self.locale, self.current_user, current_company, team, self.params, 3, True)

        templates = data.templates
        share_cover_url = templates[0].data[0].get('media_url') or \
                          self.static_url(self.current_user.company.logo)
        share_cover = self.share_url(url_append_query(share_cover_url, "imageMogr2/thumbnail/!300x300r"))

        templates_opt = list()
        for template in templates:
            if template.get("type", 0) == 4:
                continue
                # 其他团队，暂时不需要
                # 其他团队,调整链接
                # for item in template["data"]:
                #     team_id = re.match(r"\/m\/company\/team\/(\d+)", item.get("link"))
                #     item['link'] = self.make_url(path.GAMMA_POSITION_TEAM.format(int(team_id.group(1))))

            if template.get("type", 0) == 3:
                # 不需要团队在招职位
                continue

            templates_opt.append(template)

        return templates_opt, share_cover
