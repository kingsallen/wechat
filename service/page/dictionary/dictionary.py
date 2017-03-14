# coding=utf-8

from service.page.base import PageService
from conf.common import CONSTANT_PARENT_CODE
import tornado.gen


class DictionaryPageService(PageService):

    @tornado.gen.coroutine
    def get_cities(self):
        ret = yield self.infra_dict_ds.get_cities()
        return ret

    @tornado.gen.coroutine
    def get_functions(self, code):
        ret = yield self.infra_dict_ds.get_functions(code)
        return ret

    @tornado.gen.coroutine
    def get_industries(self):
        ret = yield self.infra_dict_ds.get_industries()
        return ret

    @tornado.gen.coroutine
    def get_constants(self, parent_code):
        ret = yield self.infra_dict_ds.get_const_dict(parent_code=parent_code)
        return ret

    @tornado.gen.coroutine
    def get_degrees(self):
        ret = yield self.get_constants(parent_code=CONSTANT_PARENT_CODE.DEGREE_USER)
        return ret

    @tornado.gen.coroutine
    def get_colleges(self):
        ret = yield self.infra_dict_ds.get_colleges()
        return ret
