# coding=utf-8

from service.page.base import PageService
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
