# coding=utf-8

from tornado import gen
from service.page.base import PageService
from util.common import ObjectDict
from util.tool.http_tool import http_post


class ApplicationPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_application(self, position_id, user_id):
        """返回用户申请的职位"""

        ret = yield self.job_application_ds.get_job_application(conds={
            "position_id": position_id,
            "applier_id": user_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def is_allowed_apply_position(self, user_id, company_id):
        """获取一个月内该用户再该用户的申请数量
        返回该用户是否可申请该职位
        reference: https://wiki.moseeker.com/application-api.md
        :param user_id: 求职者 id
        :param company_id: 公司 id
        :return:
        {
          'message': '提示信息',
          'status': 0,
          'data': true/false   # ture 表示命中限制，不能投递，false 表示可以投递
        }

        """

        req = ObjectDict({
            'user_id': user_id,
            'company_id': company_id,
        })
        try:
            bool_res = True
            ret = yield http_post(self.path.APPLICATION_APPLY_COUNT, req)
            bool_res = ret.data if ret.status == 0 else True
        except Exception as error:
            self.logger.warning(error)

        raise gen.Return(bool_res)
