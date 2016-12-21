# coding=utf-8

import tornado.testing
import app


class TestHandler(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        return app.make_app()

    def test_root(self):
        with tornado.testing.ExpectLog('tornado.access', "404"):
            response = self.fetch('/')
            self.assertEqual(response.code, 404)
