# coding=utf-8

from functools import partial

import tornado.gen as gen
from tornado.escape import json_encode

from handler.base import BaseHandler
from util.tool.str_tool import pinyin_match


class SuggestCompanyHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        result, companies = yield self.company_ps.get_cp_for_sug_wechat()
        s = self.params.s
        if result and s:

            company_names = filter(
                partial(pinyin_match, search=s),
                map(lambda x: x.get("name"), companies))
            companies = filter(
                lambda x: x.get("name") in company_names, companies)
            self.write(json_encode(companies))
        else:
            self.write(json_encode([]))

class SuggestCollegeHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        colleges = yield self.dictionary_ps.get_colleges()
        s = self.params.s
        if s:
            college_names = list(
                filter(partial(pinyin_match, search=s),
                map(lambda x: x.get("name"), colleges))
            )

            colleges = list(
                filter(lambda x: x.get("name") in college_names, colleges))

            self.write(json_encode(colleges))
        else:
            self.write(json_encode([]))
