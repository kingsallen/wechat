# -*- coding=utf-8 -*-

import json
from tornado import gen
from handler.base import BaseHandler



class TestCompanyVisitReqHandler(BaseHandler):

    @gen.coroutine
    def get(self):

        return
        # raise gen.Return(json.dumps(user))
