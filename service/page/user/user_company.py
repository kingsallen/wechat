# coding=utf-8

# Copyright 2016 MoSeeker

import re
from tornado.util import ObjectDict
from tornado import gen
from service.page.base import PageService

class UserCompanyPageService(PageService):

    @gen.coroutine
    def get_company_follows(self, conds, fields=[]):
        fans = yield self.wx_user_company_ds.get_user(conds)
        raise gen.Return(fans)
