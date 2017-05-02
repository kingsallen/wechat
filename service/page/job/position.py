# coding=utf-8

from tornado import gen

from service.page.base import PageService
import conf.common as const
from service.page.user.user import UserPageService
from util.common import ObjectDict
from util.common.cipher import encode_id
from util.tool.date_tool import jd_update_date, str_2_date
from util.tool.str_tool import gen_salary, split, set_literl, gen_degree, gen_experience
from util.tool.temp_data_tool import make_position_detail_cms, make_team, template3


class PositionPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_position(self, position_id):
        position = ObjectDict()
        position_res = yield self.job_position_ds.get_position({
            'id': position_id
        })

        position_ext_res = yield self.job_position_ext_ds.get_position_ext({
            "pid": position_id
        })

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
            "experience": gen_experience(position_res.experience, position_res.experience_above),
            "language": position_res.language,
            "count": position_res.count,
            "degree": gen_degree(position_res.degree, position_res.degree_above),
            "management": position_res.management,
            "visitnum": position_res.visitnum,
            "accountabilities": position_res.accountabilities,
            "requirement":      position_res.requirement,
            "feature":          position_res.feature,
            "status":           position_res.status,
            "publisher":        position_res.publisher,
            "source":           position_res.source,
            "share_tpl_id":     position_res.share_tpl_id,
            "hb_status":        position_res.hb_status,
            "team_id":          position_res.team_id,
            "app_cv_config_id": position_res.app_cv_config_id,
            "email_resume_conf": position_res.email_resume_conf
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
            self.logger.debug("")
            position.share_title = share_conf.title
            position.share_description = share_conf.description

        # 职能自定义字段（自定义字段 job_occupation）
        if position_ext_res.job_occupation_id:
            job_occupation_res = yield self.job_occupation_ds.get_occupation(conds={"id": position_ext_res.job_occupation_id})
            position.job_occupation = job_occupation_res.name

        # 属性自定义字段（自定义字段 job_custom）
        if position_ext_res.job_custom_id:
            job_custom_res = yield self.job_custom_ds.get_custom(conds={"id": position_ext_res.job_custom_id})
            position.job_custom = job_custom_res.name

        raise gen.Return(position)

    @gen.coroutine
    def update_position(self, conds, fields):
        response = yield self.job_position_ds.update_position(conds, fields)
        raise gen.Return(response)

    @staticmethod
    def _make_recom(user_id):
        """用于微信分享和职位推荐时，传出的 recom 参数"""
        if user_id is None:
            return ""
        return encode_id(user_id)

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
    def is_position_stared_by(self, user_id, position_id):
        """返回用户是否收藏了职位"""

        if user_id is None or not position_id:
            raise gen.Return(self.constant.NO)

        ret = yield self.thrift_searchcondition_ds.get_collect_position(user_id, position_id)
        raise gen.Return(self.constant.YES if ret.userCollectPosition else self.constant.NO)

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
    def get_hr_info_by_wxuser_id(self, wxuser_id):
        """获取 hr 信息"""
        hr_account = yield self.user_hr_account_ds.get_hr_account({
            "wxuser_id": wxuser_id
        })

        raise gen.Return(hr_account)

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
        :param position_id: 职位 id
        """

        pos_recommends = yield self.infra_position_ds.get_recommend_positions(position_id=position_id)
        raise gen.Return(pos_recommends)

    @gen.coroutine
    def add_reward_for_recom_click(self, employee, company_id, berecom_wxuser_id, berecom_user_id, position_id):
        """转发被点击添加积分"""

        points_conf = yield self.hr_points_conf_ds.get_points_conf(conds={
            "company_id": company_id,
            "template_id": self.constant.RECRUIT_STATUS_RECOMCLICK_ID,
        }, appends=["ORDER BY id DESC", "LIMIT 1"])

        click_record = yield self.user_employee_points_record_ds.get_user_employee_points_record(conds={
            "berecom_user_id": berecom_user_id,
            "position_id": position_id,
            "award_config_id": points_conf.id,
            "employee_id": employee.id
        }, fields=["id"])

        # 转发被点击添加积分，同一个职位，相同的人点击多次不加积分
        if not click_record:
            be_recom_wxuser = yield self.user_wx_user_ds.get_wxuser(
                {'id': berecom_wxuser_id})

            user_ps = UserPageService()
            yield user_ps.employee_add_reward(
                employee_id=employee.id,
                company_id=company_id,
                position_id=position_id,
                be_recom_wxuser=be_recom_wxuser,
                award_type=const.EMPLOYEE_AWARD_TYPE_SHARE_CLICK
            )

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
                res = make_position_detail_cms(cms_media, res_dict, module_name)
        return res

    @gen.coroutine
    def get_team_data(self, team, more_link, teamname_custom):
        team_members = yield self.hr_team_member_ds.get_team_member_list(
            conds={'team_id': team.id, 'disable': 0}
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

    @staticmethod
    def limited_company_info(current_company):
        """返回一个 company 的数据子集，用于职位列表的渲染"""
        return (ObjectDict(
            logo=current_company.logo,
            abbreviation=current_company.abbreviation or '',
            industry=current_company.industry or '',
            scale_name=const.SCALE.get(str(current_company.scale), ''),
            homepage=current_company.homepage or '',
            banner=current_company.banner,
            id=current_company.id,
        ))

    @gen.coroutine
    def infra_get_position_list(self, params):
        """普通职位列表"""

        # get position ds
        res = yield self.infra_position_ds.get_position_list(params)
        # get team names
        team_name_dict = yield self.get_teamid_names_dict(params.company_id)

        if res.status == 0:
            position_list = [ObjectDict(e) for e in res.data]
            pids = [e.id for e in position_list]
            pid_teamid_dict = yield self.get_pid_teamid_dict(params.company_id, pids)

            for position in position_list:
                position.salary = gen_salary(position.salary_top, position.salary_bottom)
                position.publish_date = jd_update_date(
                    str_2_date(position.publish_date, self.constant.TIME_FORMAT))
                position.team_name = team_name_dict.get(pid_teamid_dict.get(position.id, 0), '')

            self.logger.debug('position_list: %s' % position_list)
            return position_list
        return res

    @gen.coroutine
    def infra_get_position_list_rp_ext(self, position_list):
        """获取职位的红包信息"""

        pids_str = ','.join([str(e.id) for e in position_list])
        params = dict(pids=pids_str)
        res = yield self.infra_position_ds.get_position_list_rp_ext(params)
        if res.status == 0:
            raise gen.Return([ObjectDict(e) for e in res.data])
        raise gen.Return(res)

    @gen.coroutine
    def infra_get_rp_position_list(self, params):
        """红包职位列表"""
        res = yield self.infra_position_ds.get_rp_position_list(params)
        team_name_dict = yield self.get_teamid_names_dict(params.company_id)

        if res.status == 0:
            rp_position_list = [ObjectDict(e) for e in res.data]
            pids = [e.id for e in rp_position_list]
            pid_teamid_dict = yield self.get_pid_teamid_dict(params.company_id,pids)

            for position in rp_position_list:
                position.is_rp_reward = True
                position.salary = gen_salary(
                    position.salary_top, position.salary_bottom)
                position.publish_date = jd_update_date(str_2_date(position.publish_date, self.constant.TIME_FORMAT))
                position.team_name = team_name_dict.get(pid_teamid_dict.get(position.id, 0), '')
            return rp_position_list
        return res

    @gen.coroutine
    def infra_get_rp_share_info(self, params):
        """红包职位列表的分享信息"""
        res = yield self.infra_position_ds.get_rp_share_info(params)
        if res.status == 0:
            raise gen.Return(res.data)
        raise gen.Return(res)

    @gen.coroutine
    def get_teamid_names_dict(self, company_id):
        """获取 {<team_id>: <team_name>} 字典"""
        res_team_names = yield self.hr_team_ds.get_team_list(
            conds={'company_id': company_id,
                   'disable':    const.OLD_YES},
            fields=['id', 'name']
        )
        team_name_dict = {e.id: e.name for e in res_team_names}
        self.logger.debug('team_name_dict: %s' % team_name_dict)
        return team_name_dict

    @gen.coroutine
    def get_pid_teamid_dict(self, company_id, list_of_pid=None):
        """获取 {<position_id>: <team_id>} 字典
        """

        param = dict(
            conds={'status':     const.OLD_YES,
                   'company_id': company_id},
            fields=['id', 'team_id']
        )
        if list_of_pid and isinstance(list_of_pid, list):
            param.update(appends=["and id in %s" % set_literl(list_of_pid)])

        pid_teamid_list = yield self.job_position_ds.get_positions_list(**param)
        pid_teamid_dict = {e.id: e.team_id for e in pid_teamid_list}
        self.logger.debug('pid_teamid_dict: %s' % pid_teamid_dict)
        return pid_teamid_dict
