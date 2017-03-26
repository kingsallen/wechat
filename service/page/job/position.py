# coding=utf-8

# Copyright 2016 MoSeeker

import json
from tornado import gen

import conf.common as const
from service.page.base import PageService
from util.common import ObjectDict
from util.tool.date_tool import jd_update_date
from util.tool.http_tool import http_get, async_das_get
from util.tool.str_tool import gen_salary, split
from util.tool.temp_data_tool import make_mate, make_team, template3


class PositionPageService(PageService):
    def __init__(self, logger):
        super().__init__(logger)

    @gen.coroutine
    def get_position(self, position_id, fields=None):

        fields = fields or []
        position = ObjectDict()
        position_res = yield self.job_position_ds.get_position({
            'id': position_id
        }, fields)

        position_ext_res = yield self.job_position_ext_ds.get_position_ext({
            "pid": position_id
        }, fields)

        if not position_res:
            raise gen.Return(position)

        # 前置处理
        # 更新时间
        update_time = jd_update_date(position_res.update_time)
        # 月薪
        salary = gen_salary(position_res.salary_top, position_res.salary_bottom)

        # 职位基础信息拼装
        position = ObjectDict({
            'id': position_res.id,
            'title': position_res.title,
            'company_id': position_res.company_id,
            'department': position_res.department,
            'candidate_source': self.constant.CANDIDATE_SOURCE.get(str(position_res.candidate_source)),
            'employment_type': self.constant.EMPLOYMENT_TYPE.get(str(position_res.employment_type)),
            'update_time': update_time,
            'update_time_ori': position_res.update_time,  # 没有被处理过的原始的更新时间
            "salary": salary,
            "city": position_res.city,
            "occupation": position_res.occupation,
            "experience": position_res.experience + (
            self.constant.EXPERIENCE_UNIT if position_res.experience else '') + (
                          self.constant.POSITION_ABOVE if position_res.experience_above else ''),
            "language": position_res.language,
            "count": position_res.count,
            "degree": self.constant.DEGREE.get(str(position_res.degree)) + (
            self.constant.POSITION_ABOVE if position_res.degree_above else ''),
            "management": position_res.management,
            "visitnum": position_res.visitnum,
            "accountabilities": position_res.accountabilities,
            "requirement": position_res.requirement,
            "feature": position_res.feature,
            "status": position_res.status,
            "publisher": position_res.publisher,
            "source": position_res.source,
            "share_tpl_id": position_res.share_tpl_id,
            "hb_status": position_res.hb_status,
            "team_id": position_res.team_id
        })

        # 后置处理：
        # 福利特色 需要分割

        if position_res.feature:
            position.feature = split(position_res.feature, ["#"])

        # 需要折行
        if position_res.accountabilities:
            position.accountabilities = split(position_res.accountabilities)
        if position.requirement:
            position.requirement = split(position_res.requirement)

        # 自定义分享模板
        if position_res.share_tpl_id:
            share_conf = yield self.__get_share_conf(position_res.share_tpl_id)
            position.share_title = share_conf.title
            position.share_description = share_conf.share_description

        # 职位自定义字段
        if position_ext_res.job_custom_id:
            job_custom_res = yield self.job_custom_ds.get_custom(conds={"id": position_ext_res.job_custom_id})
            position.job_custom = job_custom_res.name

        raise gen.Return(position)

    @gen.coroutine
    def update_position(self, conds, fields):
        response = yield self.job_position_ds.update_position(conds, fields)
        raise gen.Return(response)

    @gen.coroutine
    def get_positions_list(self, conds, fields, options=[], appends=[]):

        """
        获得职位列表
        :param conds:
        :param fields:
        :param options:
        :param appends:
        :return:
        """

        positions_list = yield self.job_position_ds.get_positions_list(conds, fields, options, appends)
        raise gen.Return(positions_list)

    @gen.coroutine
    def is_position_stared_by(self, position_id, user_id):
        """返回用户是否收藏了职位"""

        fav = yield self.user_fav_position_ds.get_user_fav_position({
            "position_id": position_id,
            "sysuser_id": user_id,
            "favorite": const.FAV_YES
        })

        raise gen.Return(const.YES if fav else const.NO)

    @gen.coroutine
    def get_hr_info(self, publisher):
        """获取 hr 信息"""
        hr_account = yield self.user_hr_account_ds.get_hr_account({
            "id": publisher
        })
        if hr_account.wxuser_id:
            hr_wx_user = yield self.user_wx_user_ds.get_wxuser({
                "id": hr_account.wxuser_id
            })
        else:
            hr_wx_user = ObjectDict()
        raise gen.Return((hr_account, hr_wx_user))

    @gen.coroutine
    def __get_share_conf(self, conf_id):
        """获取职位自定义分享模板"""
        ret = yield self.job_position_share_tpl_conf_ds.get_share_conf({
            "id": conf_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_recommend_positions(self, position_id):
        """获得 JD 页推荐职位
        reference: https://wiki.moseeker.com/position-api.md#recommended

        :param position_id: 职位 id
        """

        req = ObjectDict({
            'pid': position_id,
        })
        try:
            response = list()
            ret = yield http_get(self.path.POSITION_RECOMMEND, req)
            if ret.status == 0:
                response = ret.data
        except Exception as error:
            self.logger.warn(error)

        raise gen.Return(response)

    @gen.coroutine
    def add_reward_for_recom_click(self,
                                   employee,
                                   company_id,
                                   berecom_wxuser_id,
                                   berecom_user_id,
                                   position_id):
        """转发被点击添加积分"""

        points_conf = yield self.hr_points_conf_ds.get_points_conf(conds={
            "company_id": company_id,
            "template_id": const.RECRUIT_STATUS_RECOMCLICK_ID,
        }, appends=["ORDER BY id DESC", "LIMIT 1"])

        click_record = yield self.user_employee_points_record_ds.get_user_employee_points_record_cnt(conds={
            "berecom_user_id": berecom_user_id,
            "position_id": position_id,
            "award_config_id": points_conf.id
        }, fields=["id"])

        # 转发被点击添加积分，同一个职位，相同的人点击多次不加积分
        if click_record.count_id < 1:
            yield self.user_employee_points_record_ds.create_user_employee_points_record(fields={
                "employee_id": employee.id,
                "reason": points_conf.status_name,
                "award": points_conf.reward,
                "recom_wxuser": employee.wxuser_id,
                "recom_user_id": employee.sysuser_id,
                "berecom_wxuser_id": berecom_wxuser_id,
                "berecom_user_id": berecom_user_id,
                "position_id": position_id,
                "award_config_id": points_conf.id,
            })

            # 更新员工的积分
            employee_sum = yield self.user_employee_points_record_ds.get_user_employee_points_record_sum(conds={
                "employee_id": employee.id
            }, fields=["award"])

            if employee_sum.sum_award:
                yield self.user_employee_ds.update_employee(conds={
                    "id": employee.id,
                    "company_id": company_id,
                }, fields={
                    "award": int(employee_sum.sum_award),
                })

    @gen.coroutine
    def send_candidate_view_position(self, params):
        """刷新候选人链路信息
        暂时调用 DAS，后续迁移到基础服务"""

        self.logger.debug("send_candidate_view_position: %s" % params)
        try:
            yield async_das_get("candidate/glancePosition", params)
        except Exception as error:
            self.logger.warn(error)

    # @gen.coroutine
    # def get_mate_data(self, jd_media):
    #     job_media = json.loads(jd_media)
    #     if isinstance(job_media, list) and job_media:
    #         media_list = yield self.hr_media_ds.get_media_by_ids(job_media, True)
    #         res_dict = yield self.hr_resource_ds.get_resource_by_ids(
    #             [m.res_id for m in media_list])
    #         res = make_mate(media_list, res_dict)
    #     else:
    #         res = None
    #
    #     raise gen.Return(res)

    @gen.coroutine
    def get_cms_page(self, team_id):
        res = None
        cms_page = yield self.hr_cms_pages_ds.get_page(conds={
            "config_id": team_id,
            "type": self.constant.CMS_PAGES_TYPE_POSITION_DETAIL,
            "disable": 0
        })
        if cms_page:
            page_id = cms_page.id
            cms_module = yield self.hr_cms_module_ds.get_module({
                "page_id": page_id,
                "disable": 0
            })
            if cms_module:
                module_id = cms_module.id
                module_name = cms_module.module_name
                cms_media = yield self.hr_cms_media_ds.get_media_list(conds={
                    "disable": 0,
                    "module_id": module_id
                })
                res_ids = [m.res_id for m in cms_media]
                res_dict = yield self.hr_resource_ds.get_resource_by_ids(res_ids)
                res = make_mate(cms_media, res_dict, module_name)
        return res

    @gen.coroutine
    def get_team_data(self, team, more_link, teamname_custom):
        team_members = yield self.hr_team_member_ds.get_team_member_list(
            conds={'team_id': team.id}
        )
        resources = yield self.hr_resource_ds.get_resource_by_ids(
            id_list=[m.res_id for m in team_members] + [team.res_id]
        )
        res = make_team(team, resources, more_link, team_members, teamname_custom)

        raise gen.Return(res)

    @gen.coroutine
    def get_team_position(self, team_id, handler_params, current_position_id, company_id, teamname_custom):
        positions = yield self.job_position_ds.get_positions_list(
            conds={'id': [current_position_id, '<>'],
                   'company_id': company_id,
                   'team_id': team_id,
                   'status': 0})

        if not positions:
            raise gen.Return(None)

        res = template3(title='我们' + teamname_custom['teamname_custom'] + '还需要', resource_list=positions,
                        handler_params=handler_params)

        raise gen.Return(res)
