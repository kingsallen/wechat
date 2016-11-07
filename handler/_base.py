# coding=utf-8

# Copyright 2016 MoSeeker

# 临时饭饭

import os
import re
import glob
import importlib
import ujson
import time
from tornado import gen, web
from tornado.util import ObjectDict
from app import logger

import conf.common as constant
import conf.platform as plat_constant
import conf.qx as qx_constant
import conf.help as help_constant
from util.tool.url_tool import make_static_url
from util.tool.str_tool import to_str

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
            'service.page.{0}.{1}'.format(p, m)), pmPS)(logger)
    })

MetaBaseHandler = type("MetaBaseHandler", (web.RequestHandler,), obDict)

class BaseHandler(MetaBaseHandler):

    # Initialization and properties
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.json_args = None
        self.params = self._get_params()
        self._log_info = None
        self.start_time = time.time()

    @property
    def logger(self):
        return self.application.logger

    @property
    def settings(self):
        return self.application.settings

    @property
    def constant(self):
        return constant

    @property
    def plat_constant(self):
        return plat_constant

    @property
    def qx_constant(self):
        return qx_constant

    @property
    def log_info(self):
        if self._log_info and dict(self._log_info):
            return self._log_info
        return None

    @log_info.setter
    def log_info(self, value):
        if dict(value):
            self._log_info = dict(value)

    # Public API
    def prepare(self):
        self.json_args = None
        headers = self.request.headers
        try:
            if("application/json" in headers.get("Content-Type", "") and
               self.request.body != ""):
                self.json_args = ujson.loads(self.request.body)
        except Exception as e:
            self.logger.error(e)

    # noinspection PyTypeChecker
    def _get_params(self):
        """To get all GET or POST arguments from http request
        """
        params = ObjectDict(self.request.arguments)
        for key in params:
            if isinstance(params[key], list) and params[key]:
                params[to_str(key)] = to_str(params[key][0])
        return params

    # def guarantee(self, fields_mapping, *args):
    #     self.params = {}
    #     for arg in args:
    #         try:
    #             self.params[arg] = self.json_args[arg]
    #             self.json_args.pop(arg)
    #         except KeyError:
    #             ret_field = fields_mapping.get(arg, arg)
    #             raise AttributeError(u"{0}不能为空".format(ret_field))
    #         self.params.update(self.json_args)
    #
    #     return self.params

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

    # def on_finish(self):
    #     info = ObjectDict(
    #         handler=__name__ + '.' + self.__class__.__name__,
    #         module=self.__class__.__module__.split(".")[1],
    #         status_code=self.get_status()
    #     )
    #
    #     if self.log_info:
    #         info.update(self.log_info)
    #
    #     self.logger.record(
    #         ujson.dumps(self._get_info_header(info), ensure_ascii=0))

    def write_error(self, status_code, **kwargs):

        # TODO 暂时添加错误页面
        self.render("refer/common/info.html", status_code=status_code, css="warning", info="Ta在地球上消失了")

        return



        # if status_code == 403:
        #     self.render('error/404.html',
        #                 status_code=status_code,
        #                 message="",
        #                 title=status_code)
        # elif status_code == 404:
        #     self.render('error/404.html',
        #                 status_code=status_code,
        #                 message="",
        #                 title=status_code)
        # else:
        #     self.render('error/500.html',
        #                 status_code=status_code,
        #                 message="",
        #                 title=status_code)

    def render(self, template_name, status_code=200, **kwargs):
        # self.log_info = {"res_type": "html"}
        # self.set_status(status_code)
        super(BaseHandler, self).render(template_name, **kwargs)
        return

    def send_json(self, chunk, status_code=200):
        self.log_info = {"res_type": "json"}
        chunk = ujson.encode(chunk)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_status(status_code)
        self.write(chunk)
        return

    def static_url(self, path, protocol='https'):
        """获取 static_url"""
        return make_static_url(path, protocol)

    # def _get_info_header(self, log_params):
    #     request = self.request
    #     req_params = request.arguments
    #
    #     if req_params and req_params.get('password', 0) != 0:
    #         req_params['password'] = 'xxxxxx'
    #
    #     log_info_common = ObjectDict(
    #         elapsed_time="%.4f" % (time.time() - self.start_time),
    #         useragent=request.headers.get('User-Agent'),
    #         referer=request.headers.get('Referer'),
    #         remote_ip=(
    #             request.headers.get('Remoteip') or
    #             request.headers.get('X-Forwarded-For') or
    #             request.remote_ip
    #         ),
    #         req_type=request.method,
    #         req_uri=request.uri,
    #         req_params=req_params,
    #         session_id=self.get_secure_cookie('session_id'),
    #     )
    #
    #     log_params.update(log_info_common)
    #     return ujson.encode(log_params)
