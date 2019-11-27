# coding=utf-8

import itertools
import operator
import functools

from tornado import gen

from conf import path
from service.page.base import PageService
from service.page.customize.customize import CustomizePageService
from tests.dev_data.user_company_config import COMPANY_CONFIG
from util.common import ObjectDict
from util.tool import temp_data_tool, iterable_tool
from util.tool.str_tool import gen_salary, split
from util.tool.url_tool import make_url, make_static_url
from util.common.decorator import log_core


class TeamPageService(PageService):
    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_sub_company(self, sub_company_id):
        sub_company = yield self.hr_company_ds.get_company(
            conds={'id': sub_company_id})

        raise gen.Return(sub_company)

    @log_core(threshold=20)
    @gen.coroutine
    def get_team_by_id(self, team_id):
        team = yield self.hr_team_ds.get_team(conds={'id': team_id, 'disable': 0})

        raise gen.Return(team)

    @gen.coroutine
    def get_team(self, conds):
        team = yield self.hr_team_ds.get_team(conds=conds)

        raise gen.Return(team)

    @gen.coroutine
    def get_team_by_name(self, department, company_id):
        team = yield self.hr_team_ds.get_team(
            conds={'company_id': company_id, 'name': department, 'disable': 0})

        raise gen.Return(team)

    @gen.coroutine
    def get_team_index(self, locale, company, handler_param, sub_flag=False, parent_company=None):
        """

        :param company: 当前需要获取数据的公司
        :param handler_param: 请求中参数
        :param sub_flag: 区分母公司和子公司标识，用以明确团队资源获取方式
        :param parent_company: 当sub_flag为True时, 表示母公司信息
        :return:
        """
        data = ObjectDict(templates=[])

        # 根据母公司，子公司区分对待，获取团队信息
        if sub_flag:
            teams = yield self._get_sub_company_teams(company.id)
        else:
            teams = yield self.hr_team_ds.get_team_list(
                conds={'company_id': company.id, 'is_show': 1, 'disable': 0, 'res_id': [0, '>']})
        teams.sort(key=lambda t: t.show_order)

        # 获取团队成员以及所需要的media信息
        team_resource_dict = yield self.hr_resource_ds.get_resource_by_ids(
            [t.res_id for t in teams])
        all_members_dict = yield self._get_all_team_members(
            [t.id for t in teams])
        member_head_img_dict = yield self.hr_resource_ds.get_resource_by_ids(
            all_members_dict.get('all_head_img_list'))

        # 拼装模板数据
        teamname_custom = parent_company.conf_teamname_custom
        # 如果是中文，使用中文"团队"，或者使用用户自定义的团队名称。
        if locale.code == 'zh_CN':
            teamname_custom.update(
                teamname_custom=locale.translate(
                    teamname_custom.teamname_custom,
                    plural_message=teamname_custom.teamname_custom, count=2
                )
            )
        # 如果是英文， 默认使用 "Teams"
        elif locale.code == 'en_US':
            teamname_custom.update(
                teamname_custom=locale.translate(
                    '团队',
                    plural_message='团队',
                    count=2
                )
            )
        else:
            assert False  # should not be here as we just support 2 above locales

        data.bottombar = teamname_custom
        data.header = temp_data_tool.make_header(locale, company, team_index=True, **teamname_custom)

        # 蓝色光标做定制化需求
        # customize_ps = CustomizePageService()
        # customize_ps.blue_focus_team_index_show_summary_not_description(parent_company, teams)

        # 解析生成团队列表页中每个团队信息子模块
        data.templates = [
            temp_data_tool.make_team_index_template(
                team=t,
                team_resource=team_resource_dict.get(t.res_id),
                more_link=make_url(path.TEAM_PATH.format(t.id), handler_param, self.settings.platform_host),
                member_list=[
                    temp_data_tool.make_team_member(
                        member=m,
                        head_img=member_head_img_dict.get(m.res_id)
                    ) for m in all_members_dict.get(t.id)
                ]
            ) for t in teams
        ]
        data.template_total = len(data.templates)

        raise gen.Return(data)

    @gen.coroutine
    def get_team_detail(self, locale, user, company, team, handler_param, position_num=3, is_gamma=False):
        """

        :param user: handler中的current_user
        :param company: 当前需要获取数据的公司
        :param team: 当前需要获取详情的team
        :param handler_param: 请求中参数
        :param position_num: 该团队在招职位的展示数量
        :param is_gamma: 是否来自 gamma 需求
        :return:
        """
        data = ObjectDict()

        # 根据母公司，子公司区分对待，获取对应的职位信息，其他团队信息
        position_fields = 'id title status city team_id \
                           salary_bottom salary_top department'.split()

        if company.id != user.company.id and not is_gamma:
            # 子公司 -> 子公司所属hr(pulishers) -> positions -> teams
            company_positions = yield self._get_sub_company_positions(
                company.id, position_fields)

            # 朴素版本
            # team_positions = [p for p in company_positions if p.team_id == team.id][:position_num]
            # 高端版本, let me show you some Python skill...
            team_positions = list(filter(lambda p: p.team_id == team.id, company_positions))

            team_id_list = list(set([p.team_id for p in company_positions
                                     if p.team_id != team.id]))
            other_teams = yield self._get_sub_company_teams(
                company_id=None, team_ids=team_id_list)
        else:
            team_positions = yield self.job_position_ds.get_positions_list(
                conds={
                    'company_id': company.id,
                    'status': 0,
                    'team_id': team.id
                },
                fields=position_fields,
                appends=["ORDER BY priority asc, update_time desc"]
            )

            other_teams = yield self.hr_team_ds.get_team_list(
                conds={'id': [team.id, '<>'],
                       'company_id': company.id,
                       'is_show': 1,
                       'disable': 0})
        other_teams.sort(key=lambda t: t.show_order)

        team_members = yield self.hr_team_member_ds.get_team_member_list(
            conds='team_id = {} and disable=0 order by orders, id'.format(team.id))

        templates, medias = yield self._get_team_detail_cms(team.id)

        detail_media_list = medias
        detail_media_list.sort(key=operator.itemgetter("orders"))
        res_id_list = [m.res_id for m in team_members] + \
                      [m.res_id for m in detail_media_list] + \
                      [t.res_id for t in other_teams]
        res_id_list += [team.res_id]
        res_dict = yield self.hr_resource_ds.get_resource_by_ids(res_id_list)

        # 拼装模板数据
        teamname_custom = user.company.conf_teamname_custom
        # 如果是中文，使用中文"团队"，或者使用用户自定义的团队名称。
        if locale.code == 'zh_CN':
            teamname_custom.update(
                teamname_custom=locale.translate(
                    teamname_custom.teamname_custom,
                    plural_message=teamname_custom.teamname_custom, count=2
                )
            )
        # 如果是英文， 默认使用 "Teams"
        elif locale.code == 'en_US':
            teamname_custom.update(
                teamname_custom=locale.translate(
                    '团队',
                    plural_message='团队',
                    count=2
                )
            )
        else:
            assert False  # should not be here as we just support 2 above locales
        data.bottombar = teamname_custom
        data.header = temp_data_tool.make_header(locale, company, True, team)

        data.relation = ObjectDict()

        # 玛氏定制
        company_config = COMPANY_CONFIG.get(company.id)
        if company_config and company_config.get('custom_visit_recipe', False):
            data.relation.custom_visit_recipe = company_config.custom_visit_recipe
        else:
            data.relation.custom_visit_recipe = []

        data.templates = temp_data_tool.make_team_detail_template(
            locale,
            team,
            team_members,
            templates,
            team_positions,
            other_teams,
            res_dict,
            handler_param,
            teamname_custom=teamname_custom
        )
        data.templates_total = len(data.templates)

        raise gen.Return(data)

    @gen.coroutine
    def _get_team_detail_cms(self, team_id):
        # 默认的空值
        # 从业务要求来看, 这里有数据完整性的要求, 有cms_page, 必须有cms_module, 必须有cms_media
        # 所以, 这里还是兼容了存在脏数据的情况
        # hr_cms_pages拿团队详情页的配置信息
        cms_page = yield self.hr_cms_pages_ds.get_page(conds={
            "config_id": team_id,
            "type": self.constant.CMS_PAGES_TYPE_TEAM_DETAIL,
            "disable": 0
        })
        templates = []
        if not cms_page:
            return templates, []

        page_id = cms_page.id
        cms_modules = yield self.hr_cms_module_ds.get_module_list(conds={
            "page_id": page_id,
            "disable": 0
        })
        if not cms_modules:
            return templates, []

        cms_modules.sort(key=operator.itemgetter('orders'))
        cms_modules_ids = [m.id for m in cms_modules]
        cms_medias = yield self.hr_cms_media_ds.get_media_list(
            conds="module_id in {} and disable=0 order by orders, id".format(tuple(cms_modules_ids)).replace(',)', ')')
        )
        cms_medias_res_ids = [m.res_id for m in cms_medias]
        resources_dict = yield self.hr_resource_ds.get_resource_by_ids(cms_medias_res_ids)
        for m in cms_medias:
            res = resources_dict.get(m.res_id, False)
            m.media_url = res.res_url if res else ''
            m.media_type = res.res_type if res else 0

        cms_medias_map = iterable_tool.group(cms_medias, "module_id")
        templates = [
            getattr(temp_data_tool, "make_company_module_type_{}".format(module.type))(
                cms_medias_map.get(module.id, []),
                module.module_name, module.link)
            for module in cms_modules
        ]
        return templates, cms_medias

    @gen.coroutine
    def _get_all_team_members(self, team_id_list):
        """
        根据团队id信息，获取所有团队，所有成员
        :param team_id_list:
        :return: {
            'all_headimg_list': [hr_resource_1, hr_resource_2],
            team_id_1: [hr_team_member_1, ],
            team_id_2: [hr_team_member_2, ],
            ...
        }
        """
        if not team_id_list:
            member_list = []
        else:
            member_list = yield self.hr_team_member_ds.get_team_member_list(
                conds='team_id in {} and disable=0 order by orders, id'.format(tuple(team_id_list)).replace(',)', ')'))

        result = {tid: [] for tid in team_id_list}
        result['all_head_img_list'] = []
        for member in member_list:
            result['all_head_img_list'].append(member.res_id)
            result[member.team_id].append(member)

        raise gen.Return(result)

    @gen.coroutine
    def _get_sub_company_positions(self, company_id, fields=None):
        publishers = yield self.hr_company_account_ds.get_company_accounts_list(
            conds={'company_id': company_id})
        if not publishers:
            company_positions = []
        else:
            cond1 = "status = {}".format(self.constant.POSITION_STATUS_RECRUITING)
            cond2 = 'publisher in {}'.format(tuple(
                [p.account_id for p in publishers])).replace(',)', ')')
            company_positions = yield self.job_position_ds.get_positions_list(
                conds=" and ".join([cond1, cond2]),
                fields=fields,
                appends=["ORDER BY priority desc, update_time desc"])

        raise gen.Return(company_positions)

    @gen.coroutine
    def _get_sub_company_teams(self, company_id, team_ids=None):
        """
        获取团队信息
        当只给定company_id，通过position信息中team_id寻找出所有相关团队
        当给定team_ids时获取所有对应的团队
        :param self:
        :param company_id:
        :param team_ids:
        :return: [object_of_hr_team, ...]
        """
        if not team_ids:
            publishers = yield self.hr_company_account_ds.get_company_accounts_list(
                conds={'company_id': company_id}, fields=None)
            publisher_id_tuple = tuple([p.account_id for p in publishers])

            if not publisher_id_tuple:
                raise gen.Return([])

            team_ids = yield self.job_position_ds.get_positions_list(
                conds='publisher in {} and status = {}'.format(publisher_id_tuple,
                                                               self.constant.POSITION_STATUS_RECRUITING)
                    .replace(',)', ')'),
                fields=['team_id'], options=['DISTINCT'])
            team_id_tuple = tuple([t.team_id for t in team_ids])
        else:
            team_id_tuple = tuple(team_ids)

        if not team_id_tuple:
            raise gen.Return([])

        teams = yield self.hr_team_ds.get_team_list(
            conds='id in {} and is_show=1 and disable=0'.format(
                team_id_tuple).replace(',)', ')'))

        raise gen.Return(teams)

    @gen.coroutine
    def get_gamma_company_team(self, company_id):
        """
        获得团队在招职位数
        :param company_id:
        :return:
        """

        teams = yield self.hr_team_ds.get_team_list(
            conds={'company_id': company_id, 'is_show': 1, 'disable': 0})
        teams.sort(key=lambda t: t.show_order)

        team_list = list()
        for team in teams:
            position_cnt = yield self.job_position_ds.get_position_cnt(conds={
                "team_id": team.id,
                "status": 0
            }, fields=["id"])

            # 职位数为0不显示
            if position_cnt.get("count_id", 0) == 0:
                continue

            item = ObjectDict()
            item["name"] = team.name
            item["id"] = team.id
            item["count"] = position_cnt.get("count_id", 0)
            team_list.append(item)

        return team_list

    @gen.coroutine
    def get_gamma_team_positions(self, team_id, page_no, page_size=5):
        # gamma 团队页获得团队在招职位

        page_from = (page_no - 1) * page_size

        team_positions = yield self.job_position_ds.get_positions_list(
            conds={
                'status': 0,
                'team_id': team_id
            },
            appends=["ORDER BY update_time desc", "LIMIT %d, %d" % (page_from, page_size)]
        )

        res_list = list()
        for item in team_positions:
            pos = ObjectDict()
            pos.title = item.title
            pos.id = item.id
            pos.salary = gen_salary(item.salary_top, item.salary_bottom)
            pos.image_url = make_static_url("")
            pos.city = split(item.city, [",", "，"])
            pos.team_name = ""
            res_list.append(pos)

        return res_list
