# coding=utf-8

from tornado.util import ObjectDict
from tornado import gen
from handler.base import BaseHandler
from utils.common.decorator import handle_response_error, url_valid

class LandingHandler(BaseHandler):

    '''
    企业搜索页
    '''

    @url_valid
    @handle_response_error
    @gen.coroutine
    def get(self):
        signature = str(self.get_argument("wechat_signature", ""))
        did = str(self.get_argument("did", ""))

        if did:
            # 存在子公司，则取子公司信息
            company_id = did
        elif signature:
            conds = {'signature': signature}
            wechat = yield self.wechat_ps.get_wechat(conds)
            company_id = wechat.get("company_id")
        else:
            self.write_error(404)
            return

        company_res = yield self.company_ps.get_company(conds = {'id': company_id}, need_conf=True, fields=[])
        search_seq = yield self._get_landing_item(company_res)

        company = ObjectDict({
            "logo": self.static_url(company_res.get("logo")),
            "name": company_res.get("name"),
            "image": company_res.get("conf_search_img"),
            "search_seq" : search_seq
        })

        # self.render("refer/neo_weixin/position/company_search.html", company=company)

        self.logger.debug("current_user: %s" % self.current_user)
        self.send_json({
                "msg": self.constant.RESPONSE_SUCCESS,
                "data": {
                    "company": company
                }
            })

    @gen.coroutine
    def _get_landing_item(self, company):

        '''
        根据HR设置获得搜索页页面栏目排序
        :param search_seq:
        :return:
        '''

        res = []
        company_id = company.get("id")
        for item in company.get("conf_search_seq"):
            # 工作地点
            index = int(item.get("index"))
            if index == self.plat_constant.LANDING_INDEX_CITY:
                city = {}
                city['name'] = self.plat_constant.LANDING.get(index).get("chpe")
                city['values'] = yield self.position_ps.get_positions_cities_list(company_id)
                city['key'] = "city"
                res.append(city)

            # 薪资范围
            elif index == self.plat_constant.LANDING_INDEX_SALARY:
                salary = {}
                salary['name'] = self.plat_constant.LANDING.get(index).get("chpe")
                salary['values'] = [{"value": k, "text": v.get("name")} for k, v in sorted(self.plat_constant.SALARY.items())]
                salary['key'] = "salary"
                res.append(salary)

            # 职位职能
            elif index == self.plat_constant.LANDING_INDEX_OCCUPATION:
                occupation = {}
                occupation['name'] = self.plat_constant.LANDING.get(index).get("chpe")
                occupation['values'] = yield self.position_ps.get_positions_occupations_list(company_id)
                occupation['key'] = "occupation"
                res.append(occupation)

            # 所属部门
            elif index == self.plat_constant.LANDING_INDEX_DEPARTMENT:
                department = {}
                department['name'] = self.plat_constant.LANDING.get(index).get("chpe")
                department['values'] = yield self.position_ps.get_positions_departments_list(company_id)
                department['key'] = "department"
                res.append(department)

            # 招聘类型
            elif index == self.plat_constant.LANDING_INDEX_CANDIDATE:
                candidate_source = {}
                candidate_source['name'] = self.plat_constant.LANDING.get(index).get("chpe")
                candidate_source['values'] = [{"value": k, "text": v} for k, v in sorted(self.constant.CANDIDATE_SOURCE.items())]
                candidate_source['key'] = "candidate_source"
                res.append(candidate_source)

            # 工作性质
            elif index == self.plat_constant.LANDING_INDEX_EMPLOYMENT:
                employment_type = {}
                employment_type['name'] = self.plat_constant.LANDING.get(index).get("chpe")
                employment_type['values'] = [{"value": k, "text": v} for k, v in sorted(self.constant.EMPLOYMENT_TYPE.items())]
                employment_type['key'] = "employment_type"
                res.append(employment_type)

            # 学历要求
            elif index == self.plat_constant.LANDING_INDEX_DEGREE:
                degree = {}
                degree['name'] = self.plat_constant.LANDING.get(index).get("chpe")
                degree['values'] = [{"value": k, "text": v} for k, v in sorted(self.constant.DEGREE.items())]
                degree['key'] = "education"
                res.append(degree)

            # 子公司名称
            if index == self.plat_constant.LANGDING_INDEX_CHILD_COMPANY:
                conds = {
                    "parent_id": company_id,
                    "disable": self.constant.STATUS_INUSE
                }
                fields = ["id", "abbreviation"]
                child_company_res = yield self.company_ps.get_companys_list(conds, fields)

                # 添加母公司信息
                child_company_values = [{
                    "id": company_id,
                    "abbreviation": company.get("abbreviation")
                }]

                child_company = {}
                child_company['values'] = child_company_values + list(child_company_res)
                child_company['name'] = self.plat_constant.LANDING.get(index).get("chpe")
                child_company['key'] = "child_company"
                res.append(child_company)

            # 企业自定义字段，并且配置了企业自定义字段标题
            elif index == self.plat_constant.LANDING_INDEX_CUSTOM and company.get("conf_job_custom_title"):
                conds = {
                    "company_id": company_id,
                    "status": self.constant.STATUS_INUSE
                }
                fields = ['name']

                custom = {}
                custom['name'] = company.get("conf_job_custom_title")
                custom['values'] = yield self.job_custom_ps.get_customs_list(conds, fields)
                custom['key'] = "custom"
                res.append(custom)

        raise gen.Return(res)
