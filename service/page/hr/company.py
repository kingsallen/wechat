# coding=utf-8

# Copyright 2016 MoSeeker

import re
import ujson
import conf.common as const
from util.common import ObjectDict
from tornado import gen
from service.page.base import PageService
from util.tool.url_tool import make_static_url
from util.tool.dict_tool import sub_dict
from util.tool.str_tool import is_odd, split, gen_salary, set_literl
from util.common.decorator import log_time
from util.common.exception import InfraOperationError

cached_company_sug_wechat = None


class CompanyPageService(PageService):
    def __init__(self):
        super(CompanyPageService, self).__init__()

    @log_time
    @gen.coroutine
    def get_company(self, conds, need_conf=None, fields=None):

        """
        获得公司信息
        :param conds:
        :param fields: 示例:
        conds = {
            "id": company_id
        }
        :return:
        """

        fields = fields or []
        need_conf = need_conf or False

        # 公司主表
        company = yield self.hr_company_ds.get_company(conds, fields)
        if company is None:
            self.logger.error('get_company.conds:%s, get_company.company:%s' % (conds, company))

        # 公司副表
        if need_conf:
            conds = {
                "company_id": company.get("id"),
            }
            company_conf_res = yield self.hr_company_conf_ds.get_company_conf(conds)
            if company_conf_res is None:
                self.logger.error(
                    'get_company_conf.conds:%s, get_company_conf.company_conf_res:%s' % (conds, company_conf_res))

            # 搜索页页面栏目排序
            search_seq = []
            search_seq_tmp = re.split("#", company_conf_res.get("search_seq") or self.plat_constant.LANDING_SEQ)
            for item in search_seq_tmp:
                # 若存在自定义字段值，则更新标题
                landing = self.plat_constant.LANDING.get(int(item))
                landing["index"] = item
                if company_conf_res.get("job_custom_title") and item == self.plat_constant.LANDING_INDEX_CUSTOM:
                    landing["name"] = company_conf_res.get("job_custom_title")
                search_seq.append(landing)

            # 避免副表字段与主表重复，设置默认值。副表hr_company_conf 不一定没个主表都有
            company_conf = ObjectDict({
                "conf_theme_id": company_conf_res.get("theme_id", 5),
                "conf_hb_throttle": company_conf_res.get("hb_throttle", 10),
                "conf_app_reply": company_conf_res.get("app_reply", ""),
                "conf_employee_binding": company_conf_res.get("employee_binding", ""),
                "conf_recommend_presentee": company_conf_res.get("recommend_presentee", ""),
                "conf_recommend_success": company_conf_res.get("recommend_success", ""),
                "conf_forward_message": company_conf_res.get("forward_message", ""),
                "conf_job_custom_title": company_conf_res.get("job_custom_title", ""),
                "conf_search_seq": search_seq,
                "conf_search_img": company_conf_res.get("search_img", ""),
                "conf_job_occupation": company_conf_res.get("job_occupation", ""),
                "conf_newjd_status": company_conf_res.get("newjd_status", 0),
                "conf_teamname_custom": company_conf_res.get("teamname_custom", ""),  # 职位部门字段名称
                "conf_application_time": company_conf_res.get("application_time", ""),  # 新JD开通申请时间
                "conf_hr_chat": company_conf_res.get("hr_chat", 1),  # IM 聊天开关
                "conf_show_in_qx": company_conf_res.get("show_in_qx", 1),  # 公司信息、团队信息、职位信息等只在仟寻展示
                "conf_employee_slug": company_conf_res.get("employee_slug", "员工"),  # 自定义员工称谓
                "conf_display_locale": company_conf_res.get("display_locale", ""),
                "conf_veryeast_switch": company_conf_res.get("veryeast_switch", 0),  # 最佳东方简历导入开关
            })

            # 处理公司自定义团队名称
            conf_teamname_custom = company_conf.get("conf_teamname_custom")
            if conf_teamname_custom and conf_teamname_custom.strip():
                teamname_custom = ObjectDict({'teamname_custom': conf_teamname_custom.strip()})
            else:
                teamname_custom = ObjectDict({'teamname_custom': self.constant.TEAMNAME_CUSTOM_DEFAULT})
            company_conf.update(ObjectDict({"conf_teamname_custom": teamname_custom}))

            company.update(company_conf)

        # 处理公司规模
        if company.scale:
            company.scale_name = self.constant.SCALE.get(str(company.scale))

        # 处理公司默认 logo
        if not company.logo:
            company.logo = const.COMPANY_HEADIMG

        # 处理 impression:
        if company.impression:
            impression = ujson.decode(company.impression)
            impression = sorted(impression.items(), key=lambda x: x)
            company.impression = [make_static_url(item[1]) for item in impression]

        # 处理 banner
        if company.banner:
            company.banner = [make_static_url(item) for item in ujson.decode(company.banner).values()]

        raise gen.Return(company)

    @gen.coroutine
    def get_companys_list(self, conds, fields, options=None, appends=None):

        """
        获得公司列表
        :param conds:
        :param fields:
        :param options:
        :param appends:
        :return:
        """

        options = options or []
        appends = appends or []

        positions_list = yield self.hr_company_ds.get_companys_list(conds, fields, options, appends)
        raise gen.Return(positions_list)

    @gen.coroutine
    def get_only_referral_reward(self, company_id):
        """获取公司是否开启只内推职位推荐产生积分"""
        res = yield self.infra_company_ds.get_only_referral_reward(company_id)
        if res.status == const.API_SUCCESS:
            data = res.data
        else:
            data = ObjectDict()
        return data

    @log_time
    @gen.coroutine
    def get_real_company_id(self, publisher, company_id):
        """获得职位所属公司id
        公司有母公司和子公司之分，
        如果取母公司，则取 current_user.company，如果取职位对应的公司（可能是子公司，可能是母公司）则使用该方法
        1.首先根据 hr_company_account 获得 hr 帐号与公司之间的关系，获得company_id
        2.如果1取不到，则直接取职位中的 company_id"""

        hr_company_account = yield self.hr_company_account_ds.get_company_account(conds={"account_id": publisher})
        if hr_company_account is None:
            self.logger.error(
                'get_real_company_id.publisher:%s, hr_company_account.company_id:%s, get_real_company_id.hr_company_account:%s' % (
                publisher, company_id, hr_company_account))
        real_company_id = hr_company_account.company_id or company_id

        raise gen.Return(real_company_id)

    @gen.coroutine
    def save_survey(self, fields, options=None, appends=None):
        """保存公司 survey， 在公司 profile 主页保存"""
        options = options or []
        appends = appends or []

        lastrowid = yield self.campaign_company_survey_ds.create_survey(fields)
        raise gen.Return(lastrowid)

    @gen.coroutine
    def create_company_on_wechat(self, record):
        result, data = yield self.infra_company_ds.create_company_on_wechat({
            "type": 1,
            "name": record.name,
            "abbreviation": record.abbreviation,
            "source": 8,  # 微信端添加
            "scale": record.scale,
            "industry": record.industry,
            "logo": record.logo
        })
        return result, data

    @gen.coroutine
    def get_cp_for_sug_wechat(self, name=None):
        """
        通过 profile 编辑出公司名称 sug
        :param name: 如果 name 有值, 通过 name 做 filter
        :return:
        """
        global cached_company_sug_wechat

        if cached_company_sug_wechat and name is None:
            return True, cached_company_sug_wechat

        params = ObjectDict(type=0, parent_id=0)
        if name is not None:
            params.update(name=name)

        result, data = yield self.infra_company_ds.get_company_all(params)

        if not result:
            return False, data
        else:
            keys = ['id', 'name', 'logo']
            result = []
            unique_names = []
            for e in data:
                e = ObjectDict(e)
                if e.name in unique_names:
                    continue
                e = ObjectDict(sub_dict(e, keys))
                result.append(e)
                unique_names.append(e.name)

            if cached_company_sug_wechat is None:
                cached_company_sug_wechat = result
            return True, result

    @gen.coroutine
    def get_company_reward_by_templateid(self, company_id, tempalte_id):
        """ 获取公司下新版积分配置 """

        res = yield self.hr_points_conf_ds.get_points_conf(conds={
            "company_id": company_id,
            "template_id": tempalte_id
        })

        if res:
            return res.reward

        return 0

    @gen.coroutine
    def get_company_positions(self, company_id, page_no=1, page_size=5):
        """
        gamma 公司主页，企业热招职位
        :param company_id:
        :param page_no:
        :param page_size:
        :return:
        """

        res_list = list()
        ret = yield self.thrift_position_ds.get_company_positions(
            company_id, page_no, page_size)
        if not ret.data:
            return res_list

        for item in ret.data:
            pos = ObjectDict()
            pos.title = item.title
            pos.id = item.id
            pos.salary = gen_salary(item.salaryTop, item.salaryBottom)
            pos.image_url = make_static_url(item.resUrl)
            pos.city = split(item.city, [",", "，"])
            pos.team_name = item.teamName
            res_list.append(pos)

        return res_list

    @gen.coroutine
    def create_company(self, params):
        """我也要招人，创建公司信息，同时必须要创建 hr 与 company 对应关系，否则 hr 平台会报错"""

        ret = yield self.infra_company_ds.create_company(params)
        status, data, message = ret.status, ret.data, ret.message
        return status, message, data

    @gen.coroutine
    def update_company(self, conds, fields):

        yield self.hr_company_ds.update_company(conds, fields)

        return True

    @gen.coroutine
    def belongs_to_group_company(self, company_id) -> bool:
        res = yield self.infra_company_ds.belongs_to_group_company(company_id)
        return res

    @gen.coroutine
    def get_group_company_list(self, company_id) -> list:
        res = yield self.infra_company_ds.get_group_company_list(company_id)

        return res

    @gen.coroutine
    def get_main_hr_info(self, company_id: int) -> dict:
        """根据company_id获取该公司主hr信息，
        如果该公司有超级账号，返回超级账号hr信息，
        如果该公司有普通账号，返回普通账号hr信息，
        如果是子公司，返回子账号HR信息，
        如果该公司没有hr信息，返回默认信息
        :param company_id: 公司id
        :return a dict with hr_info, including hr_id and hr_logo
                e.g. {'hr_id': 123, 'hr_logo': '/path/to/hr/logo.png'}
        """
        ret = dict(hr_id=0, hr_logo=make_static_url(const.HR_HEADIMG))

        main_hr_account = yield self.user_hr_account_ds.get_hr_account(
            conds={'company_id': company_id, 'disable': 1, 'account_type': 0}
        )

        if not main_hr_account:
            main_hr_account = yield self.user_hr_account_ds.get_hr_account(
                conds={'company_id': company_id, 'disable': 1,
                       'account_type': 2}
            )
        if not main_hr_account:
            hr_account = yield self.hr_company_account_ds.get_company_accounts_list(
                conds={'company_id': company_id},
                fields=['account_id']
            )
            hr_account_id = []
            for hr in hr_account:
                hr_account_id.append(hr.get('account_id'))
            main_hr_account = yield self.user_hr_account_ds.get_hr_account(
                conds={'disable': 1},
                appends=['and id in %s order by id asc' % set_literl(hr_account_id)]
            )

        assert main_hr_account
        ret.update(hr_id=main_hr_account.id)
        if main_hr_account.headimgurl:
            ret.update(hr_logo=make_static_url(main_hr_account.headimgurl))

        elif main_hr_account.wxuser_id:
            hr_wxuser = yield self.user_wx_user_ds.get_wxuser(
                conds={'id': main_hr_account.wxuser_id})
            if hr_wxuser:
                ret.update(hr_logo=make_static_url(hr_wxuser.headimgurl))

        return ret

    @gen.coroutine
    def get_crucial_info_state(self, company_id):
        """
        获取推荐人才关键信息开关状态
        :return:
        """
        ret = yield self.infra_company_ds.get_crucial_info_state(company_id)
        return ret

    @gen.coroutine
    def check_oms_switch_status(self, company_id, module_name):
        """
        检查oms控制的一系列开关状态
        :param company_id:
        :param module_name:
        :return:
        """
        res = yield self.infra_company_ds.check_oms_switch_status(company_id, module_name)
        return res

    @gen.coroutine
    def get_nearby_stores(self, company_id, longitude, latitude, radius):
        """
        获取用户指定范围内门店位置
        :return:
        """
        ret = yield self.infra_company_ds.get_nearby_stores(company_id, longitude, latitude, radius)
        if ret.code != const.NEWINFRA_API_SUCCESS:
            raise InfraOperationError(ret.message)
        return ret

    @gen.coroutine
    def get_position_lbs_info(self, company_id, longitude, latitude, radius, pid):
        """
        根据职位id获取职位的LBS信息
        :return:
        """
        ret = yield self.infra_company_ds.get_position_lbs_info(company_id, longitude, latitude, radius, pid)
        if ret.code != const.NEWINFRA_API_SUCCESS:
            raise InfraOperationError(ret.message)
        return ret

    @gen.coroutine
    def get_lbs_ip_location(self, remote_ip):
        """
        根据remote_ip获取定位信息：经纬度
        :return:
        """
        ret = yield self.infra_company_ds.get_lbs_ip_location(remote_ip)
        if not ret.rectangle:
            raise InfraOperationError(ret.info)
        return ret.rectangle
