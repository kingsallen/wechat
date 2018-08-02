# coding=utf-8

from functools import partial

import tornado.gen as gen

from handler.base import BaseHandler
from util.tool.str_tool import pinyin_match

from util.tool.dict_tool import ObjectDict, sub_dict

from util.common.decorator import check_and_apply_profile


class SuggestCompanyHandler(BaseHandler):

    @check_and_apply_profile
    @gen.coroutine
    def get(self):
        result, companies = yield self.company_ps.get_cp_for_sug_wechat()
        s = self.params.s
        if result and s:
            company_names = list(filter(partial(pinyin_match, search=s), map(lambda x: x.get("name"), companies)))
            companies = list(filter(lambda x: x.get("name") in company_names, companies))

            workexps = self.current_user.profile.get('workexps', [])
            to_append_workexps = []
            keys = ['company_id', 'company_logo', 'company_name']
            if workexps:
                for workexp in workexps:
                    to_append_workexp = ObjectDict(sub_dict(workexp, keys))
                    for k in keys:
                        to_append_workexp[k.split("_")[1]] = to_append_workexp[k]
                        to_append_workexp.pop(k, None)
                    to_append_workexps.append(to_append_workexp)

            companies = to_append_workexps + companies

            self.send_json_success(companies)
        else:
            self.send_json_success([])


class SuggestCollegeHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        s = self.params.s
        country_id = self.params.country_id
        data = yield self.dictionary_ps.get_overseas_colleges(country_id)
        colleges = data.get("list")
        if s:
            college_names = list(filter(partial(pinyin_match, search=s), map(lambda x: x.get("name"), colleges)))
            colleges = list(filter(lambda x: x.get("name") in college_names, colleges))
            self.send_json_success(colleges)
        else:
            self.send_json_success([])
