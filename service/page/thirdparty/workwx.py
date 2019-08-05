# coding=utf-8

from tornado import gen

import conf.common as const
from service.page.base import PageService
from util.common import ObjectDict



class WorkWXPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_workwx_info(self, method, appid=None, code=None, headers=None):
        params = ObjectDict()
        if method == const.JMIS_USER_INFO:
            params = ObjectDict({
                "code": code,
                "method": method
            })
        elif method == const.JMIS_SIGNATURE:
            params = ObjectDict({
                "appid": appid,
                "method": method
            })
        ret = yield self.joywok_ds.get_joywok_info(params, headers)
        return ret
