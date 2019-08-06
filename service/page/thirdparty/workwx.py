# coding=utf-8

from tornado import gen

import conf.common as const
from service.page.base import PageService
from util.common import ObjectDict



class WorkWXPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def create_workwx_user(self, method, appid=None, code=None, headers=None):
        """
        根据微信授权得到的 userinfo 创建 workwx_user
        :param userid:
        :param wechat_id:
        :param remote_ip:
        :param source:
        """
        # 查询 这个 userid 是不是已经存在
        user_record = yield self.workwx_user_ds.get_workwx_user({
            "unionid":  userinfo.unionid
        })

        # 如果存在，返回 userid
        if user_record:
            user_id = user_record.id
        else:
            # 如果不存在，创建 user_workwx 记录，返回 user_id
            params = ObjectDict()
            user_id = yield self.workwx_ds.create_workwx_user(params, headers)
        return user_id

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
