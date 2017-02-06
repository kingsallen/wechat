# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.page.base import PageService


class JobCustomPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_custom(self, conds, fields):

        """
        获得职位自定义字段
        :param conds:
        :param fields:
        :param options:
        :param appends:
        :return:
        """

        custom = yield self.job_custom_ds.get_custom(conds, fields)
        raise gen.Return(custom)
