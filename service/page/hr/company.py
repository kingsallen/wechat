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
from util.tool.str_tool import is_odd, split, gen_salary

cached_company_sug_wechat = None


class CompanyPageService(PageService):

    def __init__(self):
        super(CompanyPageService, self).__init__()

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

        # 公司副表
        if need_conf:
            conds = {
                "company_id": company.get("id"),
            }
            company_conf_res = yield self.hr_company_conf_ds.get_company_conf(conds)

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

            # 避免副表字段与主表重复
            company_conf = ObjectDict({
                "conf_theme_id": company_conf_res.get("theme_id"),
                "conf_hb_throttle": company_conf_res.get("hb_throttle"),
                "conf_app_reply": company_conf_res.get("app_reply"),
                "conf_employee_binding": company_conf_res.get("employee_binding"),
                "conf_recommend_presentee": company_conf_res.get("recommend_presentee"),
                "conf_recommend_success": company_conf_res.get("recommend_success"),
                "conf_forward_message": company_conf_res.get("forward_message"),
                "conf_job_custom_title": company_conf_res.get("job_custom_title"),
                "conf_search_seq": search_seq,
                "conf_search_img": company_conf_res.get("search_img"),
                "conf_newjd_status": company_conf_res.get("newjd_status"),
                "conf_teamname_custom": company_conf_res.get("teamname_custom"),  # 职位部门字段名称
                "conf_application_time": company_conf_res.get("application_time"),  # 新JD开通申请时间
                "conf_hr_chat": company_conf_res.get("hr_chat"),  # IM 聊天开关
                "conf_show_in_qx": company_conf_res.get("show_in_qx"),  # 公司信息、团队信息、职位信息等只在仟寻展示
            })

            self.logger.debug("company_conf_res:{}".format(company_conf_res))
            self.logger.debug("company_conf:{}".format(company_conf))

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
            company.impression = [make_static_url(item) for item in ujson.decode(company.impression).values()]

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
    def get_real_company_id(self, publisher, company_id):
        """获得职位所属公司id
        公司有母公司和子公司之分，
        如果取母公司，则取 current_user.company，如果取职位对应的公司（可能是子公司，可能是母公司）则使用该方法
        1.首先根据 hr_company_account 获得 hr 帐号与公司之间的关系，获得company_id
        2.如果1取不到，则直接取职位中的 company_id"""

        hr_company_account = yield self.hr_company_account_ds.get_company_account(conds={"account_id": publisher})
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
            "type":         1,
            "name":         record.name,
            "abbreviation": record.abbreviation,
            "source":       8,  # 微信端添加
            "scale":        record.scale,
            "industry":     record.industry,
            "logo":         record.logo
        })
        return result, data

    @staticmethod
    def emp_custom_field_refine_way(company_id):
        """通过companyid 奇偶判断员工认证自定义字段填写的途径
        奇数：认证成功后直接跳转
        偶数：认证成功后发送消息模板，点击消息模版填写
        """
        if is_odd(company_id):
            return const.EMPLOYEE_CUSTOM_FIELD_REFINE_TEMPLATE_MSG

        else:
            return const.EMPLOYEE_CUSTOM_FIELD_REFINE_REDIRECT


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
        ret = yield self.thrift_position_ds.get_company_positions(company_id, page_no, page_size)
        if not ret.data:
            return res_list

        for item in ret.data:
            pos = ObjectDict()
            pos.title=item.title
            pos.id=item.id
            pos.salary=gen_salary(item.salaryTop, item.salaryBottom)
            pos.image_url=make_static_url(item.resUrl)
            pos.city=split(item.city, [",","，"])
            pos.team_name=item.teamName
            res_list.append(pos)

        return res_list

    @gen.coroutine
    def create_company(self, params):
        """我也要招人，创建公司信息，同时必须要创建 hr 与 company 对应关系，否则 hr 平台会报错"""

        company_id = yield self.hr_company_ds.create_company({
            "type":         1,
            "name":         params.name,
            "source":       params.source,
        })

        return company_id

    @gen.coroutine
    def create_company_accounts(self, company_id, hr_id):
        """我也要招人，创建公司信息，同时必须要创建 hr 与 company 对应关系，否则 hr 平台会报错"""

        yield self.hr_company_account_ds.create_company_accounts({
            "company_id":  company_id,
            "account_id":  hr_id,
        })

        return True
