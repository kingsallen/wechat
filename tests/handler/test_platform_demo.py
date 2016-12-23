# coding=utf-8

import tornado.testing
from tornado.httputil import HTTPHeaders
import app
from app import Application
import tornado.web
from mockito import *
from tornado.log import access_log, app_log, gen_log
from util.common.log import Logger


class TestHandler(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        return app.make_app()

    def setUp(self):
        super().setUp()
        self.httpheaders = HTTPHeaders({
            "User-Agent": "MicroMessenger"
        })

    def test_access_root_and_return_404(self):
        with tornado.testing.ExpectLog(access_log, "404"):
            response = self.fetch('/')
            self.assertEqual(response.code, 404)

    def test_access_landing_page_using_wechat_ua_without_wechat_signature(self):
        response = self.fetch('/m/start', headers=self.httpheaders)
        print(response.body)

