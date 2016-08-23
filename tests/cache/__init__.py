# -*- coding: utf-8 -*-
from cache import cache
from tornado import gen
from tornado.util import ObjectDict
from tornado.testing import AsyncTestCase, gen_test, main

@cache(ttl=60)
@gen.coroutine
def get_position(self, condition):
    raise gen.Return(ObjectDict(condition))

class CacheTest(AsyncTestCase):

    @gen_test
    def test_get_position(self):

        c = yield get_position(self, ObjectDict({"id": 1, "title": "position_title"}))
        d = yield get_position(self, ObjectDict({"id": 1, "title": "position_title"}))
        e = yield get_position(self, ObjectDict({"id": 2, "title": "position_title"}))
        f = yield get_position(self, ObjectDict({"id": 3, "title": "position_title"}))
        self.assertIsInstance(c, ObjectDict)
        self.assertIsInstance(d, ObjectDict)
        self.assertIsInstance(e, ObjectDict)
        self.assertIsInstance(f, ObjectDict)

        self.assertIs(c.id, 1)
        self.assertIs(d.id, 1)
        self.assertIs(e.id, 2)
        self.assertIs(f.id, 3)

if __name__ == '__main__':
    main()
