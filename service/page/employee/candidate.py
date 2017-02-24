# coding=utf-8

from tornado import gen
from service.page.base import PageService

class CandidatePageService(PageService):

    def __init__(self):
        super().__init__()


    @gen.coroutine
    def send_candidate_view_position(self, user_id, position_id, sharechain_id):
        """刷新候选人链路信息，调用基础服务"""

        ret = yield self.thrift_candidate_ds.send_candidate_view_position(user_id, position_id, sharechain_id)
        self.logger.debug("send_candidate_view_position: %s" % ret)
        raise gen.Return(ret)
