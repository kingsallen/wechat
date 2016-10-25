# coding=utf-8

from tornado import gen
from service.page.base import PageService


class ApplicationPageService(PageService):

    def __init__(self, logger):
        super().__init__(logger)

    @gen.coroutine
    def is_applied(self, position_id, user_id):
        """返回用户是否申请了职位"""

        application = yield self.job_application_ds.get_application({
            "position_id": position_id,
            "applier_id": user_id
        })
        raise gen.Return(bool(application))
