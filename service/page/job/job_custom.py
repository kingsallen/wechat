# coding=utf-8

from tornado import gen
from service.page.base import PageService

class JobCustomPageService(PageService):

    @gen.coroutine
    def get_customs_list(self, conds, fields, options=[], appends=[]):

        '''
        获得职位自定义字段
        :param conds:
        :param fields:
        :param options:
        :param appends:
        :return:
        '''

        customs_list_res = yield self.job_custom_ds.get_customs_list(conds, fields, options, appends)
        customs_list = [item.get("name") for item in customs_list_res]
        raise gen.Return(customs_list)