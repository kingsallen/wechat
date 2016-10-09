# coding=utf-8

# Copyright 2016 MoSeeker

import os
import glob
import re

import socket
import ujson
import importlib
import time
from tornado import gen, web
from tornado.util import ObjectDict
from urlparse import urljoin

# 动态创建类,加载全局pageservice方法
obDict = {}
d = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/service/page/**/*.py"
for module in filter(lambda x: not x.endswith("init__.py"), glob.glob(d)):
    p = module.split("/")[-2]
    m = module.split("/")[-1].split(".")[0]
    m_list = [item.title() for item in re.split(u"_", m)]
    pmPS = "".join(m_list) + "PageService"
    pmObj = m + "_ps"
    obDict.update({
        pmObj: getattr(importlib.import_module('service.page.{0}.{1}'.format(p, m)), pmPS)()
    })

_base = type("_base", (web.RequestHandler,), obDict)


class BaseHandler(_base):

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.json_args = None
        self.params = None
        self._log_info = None
        self.start_time = time.time()

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
    def constant(self):
        return self.application.constant

    @property
    def plat_constant(self):
        return self.application.plat_constant

    @property
    def qx_constant(self):
        return self.application.qx_constant

    @property
    def help_constant(self):
        return self.application.help_constant

    @property
    def log_info(self):
        if self._log_info and dict(self._log_info):
            return self._log_info
        return None

    @log_info.setter
    def log_info(self, value):
        if dict(value):
            self._log_info = dict(value)

    def prepare(self):
        self.json_args = None
        headers = self.request.headers
        try:
            if("application/json" in headers.get("Content-Type", "") and
               self.request.body != ""):
                self.json_args = ujson.loads(self.request.body)
        except Exception as e:
            self.logger.error(e)

    def guarantee(self, fields_mapping, *args):
        self.params = {}
        for arg in args:
            try:
                self.params[arg] = self.json_args[arg]
                self.json_args.pop(arg)
            except KeyError:
                ret_field = fields_mapping.get(arg, arg)
                raise AttributeError(u"{0}不能为空".format(ret_field))
            self.params.update(self.json_args)

        return self.params

    @gen.coroutine
    def _get_current_wechat(self):

        """
        # TODO 获得企业微信信息
        :return:
        """

        wechat_signature = str(self.get_argument("wechat_signature", ""))
        conds = ObjectDict({
            'signature': wechat_signature
        })
        wechat = yield self.wechat_ps.get_wechat(conds=conds)

        raise gen.Return(wechat)

    @gen.coroutine
    def _get_current_company(self, company_id):

        """
        # TODO 获得企业母公司信息
        :param company_id:
        :return:
        """
        conds = ObjectDict({
            'id': company_id
        })
        company = yield self.company_ps.get_company(conds=conds, need_conf=True)
        theme = yield self.wechat_ps.get_wechat_theme({'id': company.get("conf_theme_id"), "disable": 0})
        if theme:
            company.update({
                "theme": [theme.get("background_color"),
                             theme.get("title_color"),
                             theme.get("button_color"),
                             theme.get("other_color")]
            })
        else:
            # TODO 暂时做初始化
            company.update({
                "theme": None
            })

        raise gen.Return(company)

    @gen.coroutine
    def get_current_user(self):

        """
        # TODO 暂时添加，保证企业号搜索页可以访问
        :return:
        """
        user = ObjectDict(
            company=ObjectDict(theme=None),
            wechat=ObjectDict()
        )
        wechat = yield self._get_current_wechat()
        if not wechat:
            raise gen.Return(user)
        company = yield self._get_current_company(wechat.get("company_id"))
        user.wechat = wechat
        user.company = company

        raise gen.Return(user)

    @gen.coroutine
    def get(self):

        """
        GET请求父类
        :return:
        """

    @gen.coroutine
    def post(self):

        """
        POST请求父类
        :return:
        """

    @gen.coroutine
    def put(self):

        """
        PUT请求父类，用户update类请求
        :return:
        """

    @gen.coroutine
    def delete(self):

        """
        DELETE请求父类
        :return:
        """

    def on_finish(self):
        info = ObjectDict(
            handler=__name__ + '.' + self.__class__.__name__,
            module=self.__class__.__module__.split(".")[1],
            status_code=self.get_status()
        )

        if self.log_info:
            info.update(self.log_info)

        self.logger.record(
            ujson.dumps(self._get_info_header(info), ensure_ascii=0))

    def write_error(self, status_code, **kwargs):

        '''
        错误页
        :param status_code: http_status
        :param kwargs:
        :return:

        usage：
            403（用户未被授权请求） Forbidden: Request failed because user does not have authorization to access a specific resource
            404（资源不存在）Resource not found
            500（服务器错误） Internal Server Error: Something went wrong on the server, check status site and/or report the issue
        '''

        if status_code == 403:
            self.render('refer/common/info.html',
                        status_code=status_code,
                        css="warning",
                        info="用户未被授权请求")
        elif status_code == 404:
            self.render('common/systemmessage.html',
                        status_code=status_code,
                        message="Ta在地球上消失了")
        else:
            self.render('common/systemmessage.html',
                        status_code=status_code,
                        message="正在努力维护服务器中")

    def render(self, template_name, status_code=200, **kwargs):
        self.log_info = {"res_type": "html"}
        self.set_status(status_code)
        super(BaseHandler, self).render(template_name, **kwargs)
        return

    def send_json(self, chunk, status_code=200):
        self.log_info = {"res_type": "json"}
        chunk = ujson.encode(chunk)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_status(status_code)
        self.write(chunk)
        return

    def static_url(self, path, include_host=None, **kwargs):
        """
        可通过该方法来拼接静态 url
        :param path:
        :param include_host:
        :param kwargs:
        :return:
        """

        if not path:
            return None

        if not path.startswith("http"):
            if "mid_path" in kwargs:
                path = os.path.join(kwargs['mid_path'], path)
            path = urljoin(self.settings['static_domain'], path)
        if not path.startswith("http") and include_host is not None:
            path = include_host + ":" + path

        return path

    def _get_info_header(self, log_params):
        request = self.request
        req_params = request.arguments
        type_wechat, type_mobile = self.depend_wechat()

        if req_params and req_params.get('password', 0) != 0:
            req_params['password'] = 'xxxxxx'

        log_info_common = ObjectDict(
            elapsed_time="%.4f" % (time.time() - self.start_time),
            product=self.env,
            type_wechat=type_wechat,
            type_mobile=type_mobile,
            useragent=request.headers.get('User-Agent'),
            referer=request.headers.get('Referer'),
            hostname=socket.gethostname(),
            remote_ip=(
                request.headers.get('Remoteip') or
                request.headers.get('X-Forwarded-For') or
                request.remote_ip
            ),
            req_type=request.method,
            req_uri=request.uri,
            req_params=req_params,
            session_id=self.get_secure_cookie('session_id'),
        )

        log_params.update(log_info_common)
        return log_params

    def depend_wechat(self):

        """
        判断用户UA是否为微信客户端
        :return:
        """
        wechat = self.constant.CLIENT_NON_WECHAT
        mobile = self.constant.CLIENT_TYPE_UNKNOWN

        try:
            useragent = self.request.headers.get('User-Agent')
            if "MicroMessenger" in useragent:
                if "iPhone" in useragent:
                    mobile = self.constant.CLIENT_TYPE_IOS
                elif "Android" in useragent:
                    mobile = self.constant.CLIENT_TYPE_ANDROID
                wechat = self.constant.CLIENT_WECHAT

        except Exception:
            pass

        return wechat, mobile
