# coding=utf-8

from tornado import gen
from service.page.base import PageService

class WechatPageService(PageService):

    @gen.coroutine
    def get_wechat(self, conds, fields=[]):

        '''
        获得公众号信息
        :param conds:
        :param fields: 示例:
        conds = {
            "id": wechat_id
            "signature": signature
        }
        :return:
        '''

        wechat = yield self.hr_wx_wechat_ds.get_wechat(conds, fields)

        raise gen.Return(wechat)