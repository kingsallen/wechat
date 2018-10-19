# coding=utf-8

import json

from tornado import gen, httpclient

import conf.common as const
from service.page.base import PageService
from setting import settings
from util.common import ObjectDict
from util.common.cipher import encode_id
from util.tool.date_tool import jd_update_date, str_2_date
from util.tool.str_tool import gen_salary, split, set_literl, gen_degree, gen_experience, to_str
from util.tool.temp_data_tool import make_position_detail_cms, make_team, template3
from util.tool.url_tool import make_static_url
from util.common.decorator import log_time


class PositionPageService(PageService):
    def __init__(self):
        super().__init__()

    @log_time
    @gen.coroutine
    def get_position(self, position_id, display_locale=None):
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
            'jobnumber': position_res.jobnumber,
            'company_id': position_res.company_id,
            'department': position_res.department,
            'candidate_source': self.constant.CANDIDATE_SOURCE.get(str(position_res.candidate_source)),
            'candidate_source_num': position_res.candidate_source,
            'employment_type': self.constant.EMPLOYMENT_TYPE.get(str(position_res.employment_type)),
            'management_experience': self.constant.MANAGEMENT_EXP.get(str(position_res.management_experience)),
            'update_time': update_time,
            'update_time_ori': position_res.update_time,  # 没有被处理过的原始的更新时间
            "salary": salary,
            "city": position_res.city,
            "occupation": position_res.occupation,
            "experience": gen_experience(position_res.experience, position_res.experience_above),
            "raw_experience": position_res.experience,
            "raw_experience_above": position_res.experience_above,
            "language": position_res.language,
            "count": position_res.count,
            "degree": gen_degree(position_res.degree, position_res.degree_above),
            "raw_degree": position_res.degree,
            "raw_degree_above": position_res.degree_above,
            "management": position_res.management,
            "visitnum": position_res.visitnum,
            "accountabilities": position_res.accountabilities,
            "requirement": position_res.requirement,
            "status": position_res.status,
            "publisher": position_res.publisher,
            "source": position_res.source,
            "share_tpl_id": position_res.share_tpl_id,
            "hb_status": position_res.hb_status,
            "team_id": position_res.team_id,
            "app_cv_config_id": position_res.app_cv_config_id,
            "email_resume_conf": position_res.email_resume_conf,
            "is_referral": bool(position_res.is_referral),
            "image": position_res.image
        })

        # 后置处理：
        # 需要折行
        if position_res.accountabilities:
            position.accountabilities = split(position_res.accountabilities)
        if position.requirement:
            position.requirement = split(position_res.requirement)

        # 自定义分享模板
        if position_res.share_tpl_id:
            position.share_title = ""
            position.share_description = ""

            share_conf = yield self.__get_share_conf(position_res.share_tpl_id)
            if share_conf.id > 3:  # 隐藏逻辑， id为1-3的话，说明是写死在数据库中的模版, 需要做国际化处理
                position.share_title = share_conf.title
                position.share_description = share_conf.description

        # 职能自定义字段（自定义字段 job_occupation）
        if position_ext_res.job_occupation_id:
            job_occupation_res = yield self.job_occupation_ds.get_occupation(
                conds={"id": position_ext_res.job_occupation_id})
            position.job_occupation = job_occupation_res.name

        # 属性自定义字段（自定义字段 job_custom）
        if position_ext_res.job_custom_id:
            job_custom_res = yield self.job_custom_ds.get_custom(conds={"id": position_ext_res.job_custom_id})
            position.job_custom = job_custom_res.name

        # 从 ES 中拉取职位的城市信息 （以后全部放到基础服务获取）
        data = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"id": position_id}}
                    ]
                }
            }
        }
        response = self.es.search(index='new_index', body=data)
        result_list = response.hits.hits
        city = ""
        city_ename = ""
        if result_list:
            result = result_list[0]
            source = ObjectDict(result.get("_source"))
            city = source.city
            city_ename = source.city_ename

        # 国际化
        if display_locale == "en_US":
            position.city = city_ename
            position.salary = "Salary negotiable" if position.salary == "薪资面议" else position.salary
        else:
            position.city = city
            position.salary = position.salary

        raise gen.Return(position)

    @gen.coroutine
    def get_position_custom_list(self, position_id_list):
        # 获取职位信息扩展信息列表
        position_ext_list, position_ext_id_list = yield self.get_position_ext_list(
            position_id_list)

        # 获取职位自定义字段列表
        customs_list, customs_id_list = yield self.get_customs_list(position_ext_id_list)

        position_custom_list = []
        position_custom = ObjectDict()
        for custom in customs_list:
            for ext in position_ext_list:
                if custom.id == ext.job_custom_id:
                    position_custom.id = ext.pid
                    position_custom.custom_field = custom.name
            position_custom_list.append(position_custom)
        return position_custom_list, customs_id_list

    @gen.coroutine
    def update_position(self, conds, fields):
        response = yield self.job_position_ds.update_position(conds, fields)
        raise gen.Return(response)

    @gen.coroutine
    def get_position_ext_list(self, position_id_list):
        """
        获得职位扩展信息
        :param position_id_list
        :return:
        """
        params = dict()
        position_ext_list = []
        if position_id_list and isinstance(position_id_list, list):
            params.update(conds=["pid in %s" % set_literl(position_id_list)])
            position_ext_list = yield self.job_position_ext_ds.get_position_ext_list(**params)

        position_ext_id_list = []
        if position_ext_list:
            for e in position_ext_list:
                position_ext_id_list.append(e.pid)
        return position_ext_list, position_ext_id_list

    @gen.coroutine
    def get_customs_list(self, position_ext_id_list):
        """
        获得职位自定义字段配置信息
        :param position_ext_id_list:
        :return:
        """
        params = dict()
        customs_list = []
        if position_ext_id_list and isinstance(position_ext_id_list, list):
            params.update(conds=["id in %s" % set_literl(position_ext_id_list)])
            customs_list = yield self.job_custom_ds.get_customs_list(**params)
        customs_id_list = []
        if customs_list:
            for e in customs_list:
                customs_id_list.append(e.id)
        return customs_list, customs_id_list

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

    @log_time
    @gen.coroutine
    def is_position_stared_by(self, user_id, position_id):
        """返回用户是否收藏了职位"""

        if user_id is None or not position_id:
            raise gen.Return(self.constant.NO)

        ret = yield self.thrift_searchcondition_ds.get_collect_position(user_id, position_id)

        if ret.userCollectPosition and ret.userCollectPosition.status == 0:
            raise gen.Return(self.constant.YES)
        else:
            raise gen.Return(self.constant.NO)

    @gen.coroutine
    def get_hr_info(self, publisher):
        """获取 hr 信息"""
        hr_account = yield self.user_hr_account_ds.get_hr_account({
            "id": publisher
        })
        if hr_account.wxuser_id:
            hr_wx_user = yield self.user_wx_user_ds.get_wxuser(conds={
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
    def get_hr_wx_user(self, unionid, wechat_id):
        """获取已关注hr用户"""
        hr_account = yield self.user_wx_user_ds.get_wxuser({
            "unionid": unionid,
            "wechat_id": wechat_id,
            "is_subscribe": [const.WX_USER_SUBSCRIBED, "="],
        })

        raise gen.Return(hr_account)

    @gen.coroutine
    def __get_share_conf(self, conf_id):
        """获取职位自定义分享模板"""
        ret = yield self.job_position_share_tpl_conf_ds.get_share_conf({
            "id": conf_id
        })
        raise gen.Return(ret)

    @log_time
    @gen.coroutine
    def get_recommend_positions(self, position_id):
        """获得 JD 页推荐职位
        :param position_id: 职位 id
        """

        pos_recommends = yield self.infra_position_ds.get_recommend_positions(position_id=position_id)
        raise gen.Return(pos_recommends)

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
                module_link = cms_module.link
                cms_media = yield self.hr_cms_media_ds.get_media_list(conds={
                    "disable": 0,
                    "module_id": module_id
                })
                res_ids = [m.res_id for m in cms_media]
                res_dict = yield self.hr_resource_ds.get_resource_by_ids(res_ids)
                res = make_position_detail_cms(cms_media, res_dict, module_name, module_link)
        return res

    @gen.coroutine
    def get_team_data(self, team, more_link, teamname_custom):
        res = None
        team_members = yield self.hr_team_member_ds.get_team_member_list(
            conds={'team_id': team.id, 'disable': 0}
        )
        resources = yield self.hr_resource_ds.get_resource_by_ids(
            id_list=[m.res_id for m in team_members] + [team.res_id]
        )
        if resources:
            res = make_team(team, resources, more_link, team_members, teamname_custom)

        raise gen.Return(res)

    @gen.coroutine
    def get_team_position(self, locale, team_id, handler_params, current_position_id, company_id, teamname_custom):
        positions = yield self.job_position_ds.get_positions_list(
            conds={
                'id': [current_position_id, '<>'],
                'company_id': company_id,
                'team_id': team_id,
                'status': 0
            },
            appends=["ORDER BY update_time DESC"]
        )

        if not positions:
            raise gen.Return(None)

        res = template3(
            title=locale.translate("company_our_team_need").format(teamname_custom['teamname_custom']),
            resource_list=positions,
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
    def infra_get_position_list(self, params, is_referral=None):
        """职位列表"""
        if is_referral:
            res = yield self.infra_position_ds.get_referral_position_list(params)
        else:
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
        params.update(page_from=int(params.page_from / 10) + 1)

        res = yield self.infra_position_ds.get_rp_position_list(params)

        team_name_dict = yield self.get_teamid_names_dict(params.company_id)

        if res.status == 0:
            rp_position_list = [ObjectDict(e) for e in res.data]
            pids = [e.id for e in rp_position_list]
            pid_teamid_dict = yield self.get_pid_teamid_dict(params.company_id, pids)

            for position in rp_position_list:
                position.is_rp_reward = True
                position.salary = gen_salary(
                    position.salary_top, position.salary_bottom)
                position.publish_date = jd_update_date(str_2_date(position.publish_date, self.constant.TIME_FORMAT))
                position.team_name = team_name_dict.get(pid_teamid_dict.get(position.id, 0), '')
                position.employee_only = position.employee_only
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
    def infra_get_position_employeerecom(self, infra_params, company_id):
        """
        请求基础服务, 获取员工推荐职位列表
        :param infra_params: ObjectDict({
                                'page_from': self.params.pageNo,
                                'page_size': self.params.pageSize,
                                'userId': self.current_user.sysuser.id,
                                "companyId": company_id,
                                "recomPushId": self.params.recomPushId
                            })
        :param company_id:
        :return:
        """
        try:
            res = yield self.infra_position_ds.get_position_employeerecom(infra_params)
        except Exception as e:
            self.logger.warn(e)
            return []

        if res.status == 0:
            # 获取获取到普通职位列表，则根据获取的数据查找其中红包职位的红包相关信息
            position_list = [ObjectDict(e) for e in res.data]

            # 团队信息 #
            # 逻辑和infra_get_position_personarecom一样, 代码有重复, TODO: 优化
            pids = [e.id for e in position_list]
            pid_teamid_dict = yield self.get_pid_teamid_dict(company_id, pids)
            team_name_dict = yield self.get_teamid_names_dict(company_id)
            for position in position_list:
                position.salary = gen_salary(position.salary_top, position.salary_bottom)
                position.publish_date = jd_update_date(str_2_date(position.publish_date, self.constant.TIME_FORMAT))
                position.team_name = team_name_dict.get(pid_teamid_dict.get(position.id, 0), '')

            # 职位红包 #
            # 逻辑和职位列表页一样, 代码有重复, TODO: 优化
            rp_position_list = [p for p in position_list if p.in_hb]
            if position_list and rp_position_list:
                rpext_list = yield self.infra_get_position_list_rp_ext(rp_position_list)

                for position in position_list:
                    pext = [e for e in rpext_list if e.pid == position.id]
                    if pext:
                        position.remain = pext[0].remain
                        position.employee_only = pext[0].employee_only
                        position.is_rp_reward = position.remain > 0
                    else:
                        position.is_rp_reward = False
            return position_list, res.data[0]['total_num'] if res.data else 0
        else:
            self.logger.warn(res)
            return []

    @gen.coroutine
    def infra_obtain_sug_list(self, params):
        """获取sug"""
        result, res = yield self.infra_position_ds.post_sug_list(params)
        return res

    @gen.coroutine
    def infra_get_position_personarecom(self, infra_params, company_id):
        """
        TODO: 补充文档
        :param infra_params:
        :param company_id:
        :return:
        """
        res = yield self.infra_position_ds.get_position_personarecom(infra_params)

        team_name_dict = yield self.get_teamid_names_dict(company_id)

        if res.status == 0:
            position_list = [ObjectDict(e) for e in res.data]
            pids = [e.id for e in position_list]
            pid_teamid_dict = yield self.get_pid_teamid_dict(company_id, pids)

            for position in position_list:
                position.salary = gen_salary(position.salary_top, position.salary_bottom)
                position.publish_date = jd_update_date(str_2_date(position.publish_date, self.constant.TIME_FORMAT))
                position.team_name = team_name_dict.get(pid_teamid_dict.get(position.id, 0), '')

            return position_list, res.data[0]['total_num'] if res.data else 0
        return res

    @gen.coroutine
    def get_teamid_names_dict(self, company_id):
        """获取 {<team_id>: <team_name>} 字典"""
        res_team_names = yield self.hr_team_ds.get_team_list(
            conds={'company_id': company_id,
                   'disable': const.OLD_YES},
            fields=['id', 'name']
        )
        if res_team_names is None:
            self.logger.error('get_teamid_names_dict.company_id:%s, get_teamid_names_dict.res_team_name:%s' % (
                company_id, res_team_names))
        team_name_dict = {e.id: e.name for e in res_team_names}
        return team_name_dict

    @gen.coroutine
    def get_pid_teamid_dict(self, company_id, list_of_pid=None):
        """获取 {<position_id>: <team_id>} 字典
        """

        param = dict(
            conds={'status': const.OLD_YES,
                   'company_id': company_id},
            fields=['id', 'team_id']
        )
        if list_of_pid and isinstance(list_of_pid, list):
            param.update(appends=["and id in %s" % set_literl(list_of_pid)])

        pid_teamid_list = yield self.job_position_ds.get_positions_list(**param)
        if pid_teamid_list is None:
            self.logger.error('get_pid_teamid_dict.company_id:%s, get_pid_teamid_dict.pid_teamid_list:%s' % (
                company_id, pid_teamid_list))
        pid_teamid_dict = {e.id: e.team_id for e in pid_teamid_list}
        self.logger.debug('pid_teamid_dict: %s' % pid_teamid_dict)
        return pid_teamid_dict

    @gen.coroutine
    def get_position_positions(self, position_id, page_no=1, page_size=5):
        """
        gamma JD页，职位相似职位
        :param company_id:
        :param page_no:
        :param page_size:
        :return:
        """

        res_list = list()
        ret = yield self.thrift_position_ds.get_position_positions(position_id, page_no, page_size)
        if not ret.data:
            return res_list

        for item in ret.data:
            pos = ObjectDict()
            pos.title = item.title
            pos.id = item.id
            pos.salary = gen_salary(item.salaryTop, item.salaryBottom)
            pos.image_url = make_static_url(item.resUrl)
            pos.city = item.city
            pos.team_name = item.teamName
            res_list.append(pos)

        return res_list

    @gen.coroutine
    def get_position_feature(self, position_id):
        result, data = yield self.infra_position_ds.get_position_feature(position_id)
        return data

    @gen.coroutine
    def get_recom_position_list_wx_tpl_receive(self, user_id, wechat_id):
        """获取推荐职位列表模板消息推送是否接收数据"""

        ret = yield self.infra_position_ds.get_recom_position_list_wx_tpl_receive(user_id, wechat_id)
        raise gen.Return(ret)

    @gen.coroutine
    def not_receive_recom_position_wx_tpl(self, user_id, wechat_id):
        """暂不接收推荐职位列表消息模板"""
        ret = yield self.infra_position_ds.post_not_receive_recom_position_wx_tpl(user_id, wechat_id)
        raise gen.Return(ret)

    @gen.coroutine
    def position_search_history(self, user_id, app_id):
        """搜索历史记录列表"""
        ret = yield self.infra_position_ds.get_position_search_history(user_id, app_id)
        raise gen.Return(ret)

    @gen.coroutine
    def patch_position_search_history(self, user_id, app_id):
        """清除历史记录列表"""
        ret = yield self.infra_position_ds.patch_position_search_history(user_id, app_id)
        raise gen.Return(ret)

    @gen.coroutine
    def get_position_bonus(self, pid):
        """获取职位奖金"""
        ret = yield self.infra_position_ds.get_position_bonus(pid)
        bonus = ret.data.position_bonus.get("total_bonus")
        return bonus
