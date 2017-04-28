# coding=utf-8

# @Time    : 2/6/17 15:24
# @Author  : panda (panyuxin@moseeker.com)
# @File    : metabase.py
# @DES     : 基础 Base，只包含一些公共方法，不涉及到业务逻辑，
#            仅供 BaseHandler 调用，或与 BaseHandler 不同业务逻辑时调用

# Copyright 2016 MoSeeker

import os
import re
import importlib
import glob
import time
import ujson
import socket
import urllib.parse
import tornado.httpclient

from tornado import web, gen

import conf.message as msg_const
import conf.common as const
from util.common import ObjectDict
from util.tool.dict_tool import objectdictify
from util.tool.date_tool import curr_now
from util.tool.str_tool import to_str
from util.tool.url_tool import make_static_url
from util.tool.json_tool import encode_json_dumps, json_dumps

# 动态加载所有 PageService
obDict = {}
d = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + \
    "/service/page/**/*.py"
for module in filter(lambda x: not x.endswith("init__.py"), glob.glob(d)):
    p = module.split("/")[-2]
    m = module.split("/")[-1].split(".")[0]
    m_list = [item.title() for item in re.split("_", m)]
    pmPS = "".join(m_list) + "PageService"
    pmObj = m + "_ps"
    obDict.update({
        pmObj: getattr(importlib.import_module(
            'service.page.{0}.{1}'.format(p, m)), pmPS)()
    })

AtomHandler = type("AtomHandler", (web.RequestHandler,), obDict)


class MetaBaseHandler(AtomHandler):

    """baseHandler 基类，不能被业务 hander 直接调用。除非是不能继承 BaseHandler"""

    def __init__(self, application, request, **kwargs):
        super(MetaBaseHandler, self).__init__(application, request, **kwargs)

        # 全部 arguments
        self.params = self._get_params()
        # api 使用，json arguments
        self.json_args = self._get_json_args()
        # 记录初始化的时间
        self._start_time = time.time()
        # 保存是否在微信环境，微信客户端类型
        self._in_wechat, self._client_type = self._depend_wechat()
        # 日志信息
        self._log_info = None
        # page service 初始化

    def initialize(self, event):
        # 日志需要，由 route 定义
        self._event = event

    # PROPERTIES
    @property
    def logger(self):
        return self.application.logger

    @property
    def settings(self):
        return self.application.settings

    @property
    def env(self):
        return self.application.env

    @property
    def executor(self):
        return self.application._executor

    @property
    def is_platform(self):
        return self.env == const.ENV_PLATFORM

    @property
    def is_qx(self):
        return self.env == const.ENV_QX

    @property
    def is_help(self):
        return self.env == const.ENV_HELP

    @property
    def in_wechat(self):
        return self._in_wechat == const.CLIENT_WECHAT

    @property
    def in_wechat_ios(self):
        return self.in_wechat and self._client_type == const.CLIENT_TYPE_IOS

    @property
    def in_wechat_android(self):
        return self.in_wechat and self._client_type == const.CLIENT_TYPE_ANDROID

    @property
    def host(self):
        """判断当前 host，不能简单的从 request.host获得"""
        if self.is_platform:
            host = self.settings.platform_host
        elif self.is_qx:
            host = self.settings.qx_host
        else:
            host = self.settings.helper_host

        return host

    @property
    def app_id(self):
        """appid for infra"""
        return const.APPID[self.env]

    @property
    def redis(self):
        return self.application.redis

    @property
    def log_info(self):
        return self._log_info

    @log_info.setter
    def log_info(self, value):

        if self._log_info is None:
            self._log_info = ObjectDict()

        self._log_info.update(dict(value))

    # noinspection PyTypeChecker
    def _get_params(self):
        """To get all GET or POST arguments from http request
        """
        params = ObjectDict(self.request.arguments)
        for key in params:
            if isinstance(params[key], list) and params[key]:
                params[to_str(key)] = to_str(params[key][0]).strip()
        return params

    def _get_json_args(self):
        """获取 api 调用的 json dict"""

        json_args = {}
        headers = self.request.headers
        body = self.request.body

        if (headers.get('Content-Type') and
                'application/json' in headers.get('Content-Type') and body):
            json_args = ujson.loads(to_str(body))

        return objectdictify(json_args)

    def guarantee(self, *args):
        """对 API 调用输入做参数检查

        注意: 请不要在guarantee 后直接使用 json_args 因为在执行
        guarantee 的过程中, json_args 会陆续pop 出元素.
        相对的应该使用params

        usage code view::
            try:
                self.guarantee("mobile", "name", "password")
            except AttributeError:
                return

            mobile = self.params["mobile"]
        """
        c_arg = None
        try:
            for arg in args:
                c_arg = arg
                self.params[arg] = self.json_args[arg]
                self.json_args.pop(arg)
        except KeyError as e:
            self.send_json_error(message="{}不能为空".format(c_arg),
                                 http_code=416)
            self.finish()
            self.logger.error(str(e) + " 缺失")
            raise AttributeError(str(e) + " 缺失")

        self.params.update(self.json_args)

    def get_current_user(self):
        return ObjectDict()

    # tornado hooks
    @gen.coroutine
    def get(self, *args, **kwargs):
        pass

    @gen.coroutine
    def post(self, *args, **kwargs):
        pass

    @gen.coroutine
    def put(self, *args, **kwargs):
        pass

    @gen.coroutine
    def delete(self, *args, **kwargs):
        pass

    def static_url(self, path, protocol='https'):
        """获取 static_url"""
        return make_static_url(path, protocol)

    def on_finish(self):
        """on_finish 时处理传输日志"""
        info = ObjectDict(
            handler=__name__ + '.' + self.__class__.__name__,
            module=self.__class__.__module__.split(".")[1],
        )

        if self.log_info:
            info.update(self.log_info)

        self.logger.stats(
            ujson.dumps(self._get_info_header(info), ensure_ascii=0))

        self.logger.debug(
            "mviewer_id: {}".format(self.get_secure_cookie(const.COOKIE_MVIEWERID)))
        self.logger.debug(
            "session_id: {}".format(self.get_secure_cookie(const.COOKIE_SESSIONID)))

        self.logger.debug("is_platform:{}".format(self.is_platform))
        self.logger.debug("is_qx:{}".format(self.is_qx))
        self.logger.debug("is_help:{}".format(self.is_help))
        self.logger.debug("request:{}".format(self.request))

    def write_error(self, http_code, **kwargs):
        """错误页
        403（用户未被授权请求） Forbidden: Request failed because user does not have authorization to access a specific resource
        404（资源不存在）      Resource not found
        500（服务器错误）      Internal Server Error: Something went wrong on the server, check status site and/or report the issue
        """

        template = 'system/info.html'

        if http_code == 403:
            self.render_page(template, data={
                    'code': http_code,
                    'css': 'warning',
                    'message': msg_const.NOT_AUTHORIZED
                })

        elif http_code == 404:
            self.render_page(template, data={
                    'code': http_code,
                    'message': msg_const.NO_DATA
                })
        else:
            message = kwargs.get('message') or msg_const.UNKNOWN_DEFAULT
            self.render_page(template, data={
                    'code': http_code,
                    'message':message
                })

    def render(self, status_code=const.API_SUCCESS, http_code=200, *args, **kwargs):
        """override RequestHandler.render()"""

        self.log_info = {"res_type": "html", "status_code": status_code}
        self.set_status(http_code)

        super().render(*args, **kwargs)

    def render_page(
            self,
            template_name,
            data,
            status_code=const.API_SUCCESS,
            message=msg_const.RESPONSE_SUCCESS,
            meta_title=const.PAGE_META_TITLE,
            http_code=200):
        """render 页面"""
        self.log_info = {"res_type": "html", "status_code": status_code}
        self.set_status(http_code)

        try:
            render_json = encode_json_dumps({
                "status": status_code,
                "message": message,
                "data": data
            })
        except TypeError as e:
            self.logger.error(e)
            render_json = encode_json_dumps({
                "status": const.API_FAILURE,
                "message": msg_const.RESPONSE_FAILURE,
                "data": None
            })

        else:
            # 前后端联调使用
            if self.settings.get('remote_debug', False) is True:
                template_string = self.render_string(template_name,
                                                     render_json=render_json)
                post_url = urllib.parse.urljoin(
                    self.settings.get('remote_debug_ip'), template_name)
                http_client = tornado.httpclient.HTTPClient()
                r = http_client.fetch(post_url, method="POST",
                                      body=template_string)
                self.write(r.body)
                self.finish()
                return

        super().render(
            template_name=template_name,
            render_json=render_json,
            meta_title=meta_title)
        return

    def _send_json(self, data, status_code, message, http_code=200):
        """传递 JSON 到前端 Used for API"""

        render_json = json_dumps({
            "status": status_code,
            "message": message,
            "data": data
        })

        if status_code == const.API_FAILURE and http_code == 200:
            http_code = 416

        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.log_info = {"res_type": "json", "status_code": status_code}
        self.set_status(http_code)
        self.write(render_json)

    def send_xml(self, data=None):
        """传递 xml 到前端 Used for API"""
        if data is None:
            data = ""

        self.log_info = {"res_type": "xml"}
        self.logger.debug("Wechat MSG: %s" % data)
        self.write(data)

    def send_json_success(self, data=None, message=msg_const.RESPONSE_SUCCESS,
                          http_code=200):
        """API 成功返回的便捷方法"""
        if data is None:
            data = ""

        self._send_json(data=data, status_code=const.API_SUCCESS,
                        message=message, http_code=http_code)

    def send_json_warning(self, data=None, message=msg_const.RESPONSE_WARNING,
                          http_code=200):
        """API 返回部分成功的便捷方法"""
        if data is None:
            data = ""
        self._send_json(data=data, status_code=const.API_WARNING,
                        message=message, http_code=http_code)

    def send_json_error(self, data=None, message=msg_const.RESPONSE_FAILURE,
                        http_code=416):
        """API 错误返回的便捷方法"""
        if data is None:
            data = ""
        self._send_json(data=data, status_code=const.API_FAILURE,
                        message=message, http_code=http_code)

    def _get_info_header(self, log_params):
        """构建日志内容"""

        def _readable_cookies():
            """基于 self.cookies 的内容构建一个简单可读的 dict"""
            # return ObjectDict(
            #     {k: repr(v.value) for k, v in sorted(self.cookies.items())}
            # )
            return None

        request = self.request
        req_params = request.arguments

        customs = ObjectDict(
            type_wechat=self._in_wechat,
            type_mobile=self._client_type)

        if self.current_user:
            customs.update(
                recom_id=self.current_user.get("recom", {}).get("id", 0),
                qxuser_id=self.current_user.get("qxuser", {}).get("id", 0),
                wxuser_id=self.current_user.get("wxuser", {}).get("id", 0),
                wechat_id=self.current_user.get("wechat", {}).get("id", 0))
            user_id = self.current_user.get("sysuser", {}).get("id", 0)
        else:
            user_id = 0

        log_info_common = ObjectDict(
            req_time=curr_now(),
            hostname=socket.gethostname(),
            appid=self.app_id,
            http_code=self.get_status(),
            opt_time="%.2f" % ((time.time() - self._start_time) * 1000),
            useragent=request.headers.get('User-Agent'),
            referer=request.headers.get('Referer'),
            remote_ip=(
                request.headers.get('Remoteip') or
                request.headers.get('X-Real-Ip') or
                request.remote_ip
            ),
            event="{}_{}".format(self._event, request.method),
            cookie=_readable_cookies(),
            user_id=user_id,
            req_type=request.method,
            req_uri=request.uri,
            req_params=req_params,
            customs=customs,
            session_id=to_str(self.get_secure_cookie(const.COOKIE_SESSIONID)
                              or to_str(self.get_secure_cookie(const.COOKIE_MVIEWERID)))
        )

        log_params.update(log_info_common)
        return log_params

    def _depend_wechat(self):
        """判断用户UA是否为微信客户端"""
        wechat = const.CLIENT_NON_WECHAT
        mobile = const.CLIENT_TYPE_UNKNOWN

        useragent = self.request.headers.get('User-Agent')
        if "MicroMessenger" in useragent:
            if "iPhone" in useragent:
                mobile = const.CLIENT_TYPE_IOS
            elif "Android" in useragent:
                mobile = const.CLIENT_TYPE_ANDROID
            wechat = const.CLIENT_WECHAT

        return wechat, mobile
