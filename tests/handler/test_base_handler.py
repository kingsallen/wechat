# coding=utf-8


import json
import unittest

import tornado.ioloop
from mockito import *
from tornado.http1connection import HTTP1Connection
from tornado.httputil import HTTPServerRequest, HTTPHeaders
from tornado.iostream import BaseIOStream

import conf.common as const
from app import make_app
from handler.base import BaseHandler


class TestBaseHandler(unittest.TestCase):

    def setUp(self):
        # mocks
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.stream = BaseIOStream(self.ioloop)
        self.connection = HTTP1Connection(stream=self.stream, is_client=True)
        when(self.connection).set_close_callback(any()).thenReturn(None)

        self.headers = HTTPHeaders()
        self.headers.add('User-Agent', 'MicroMessenger iPhone')

        self.request = HTTPServerRequest(
            uri='http://platform.moseeker.com/m/position/123',
            headers=self.headers,
            connection=self.connection)

        self.application = make_app()

    def tearDown(self):
        unstub()

    def test_mock(self):
        obj = mock()
        obj.say('Hi')
        verify(obj).say('Hi')
        verifyNoMoreInteractions(obj)

    def test_wechat_ios_env_info(self):
        self.handler = BaseHandler(self.application, self.request, event='test_event')
        self.assertTrue(self.handler.in_wechat_ios)
        self.assertTrue(self.handler.in_wechat)

    def test_wechat_android_env_info(self):
        self.headers = HTTPHeaders({'User-Agent': 'MicroMessenger Android'})
        self.request.headers = self.headers
        self.handler = BaseHandler(self.application, self.request, event='test_event')
        self.assertTrue(self.handler.in_wechat_android)
        self.assertTrue(self.handler.in_wechat)

    def test_outside_wechat_env_info(self):
        self.headers = HTTPHeaders({'User-Agent': 'Safari'})
        self.request.headers = self.headers
        self.handler = BaseHandler(self.application, self.request, event='test_event')
        self.assertFalse(self.handler.in_wechat)
        self.assertEqual(self.handler._in_wechat, const.CLIENT_NON_WECHAT)
        self.assertEqual(self.handler._client_type, const.CLIENT_TYPE_UNKNOWN)

    def test_json_args(self):
        self.headers.add('Content-Type', 'application/json')
        self.request.body = json.dumps({'a': 1, 'b': 2})
        self.handler = BaseHandler(self.application, self.request, event='test_event')
        self.assertDictEqual(self.handler.json_args, {'a': 1, 'b': 2})

if __name__ == '__main__':
    unittest.main()
