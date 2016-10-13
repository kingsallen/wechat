# coding=utf-8
import tornado.gen as gen
from service.page.base import PageService


class UserPageService(PageService):

    @gen.coroutine
    def binding_user(self, handler, user_id, wxuser, qxuser):
        # for qxuser:
        if user_id != wxuser.sysuser_id:
            yield self.user_wx_user_ds.update_wxuser(
                conds={"id": [wxuser.id, "="]},
                fields={"sysuser_id": user_id}
            )
        if user_id != qxuser.sysuser_id:
            yield self.user_user_ds.update_wxuser(
                conds={"id": [wxuser.id, "="]},
                fields={"sysuser_id": user_id}
            )
