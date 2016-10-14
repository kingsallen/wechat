# coding=utf-8

# Copyright 2016 MoSeeker

import os
import glob
import re

import socket
import ujson
import importlib
import time

import tornado.escape
import tornado.httpclient

from hashlib import sha1
from tornado import gen, web
from tornado.util import ObjectDict
# from tor
from urllib.parse import urljoin
from tornado.options import options
import conf.common as constant
from service.data.session.session import JsApi, Wechat, Employee, Recom, SysUser, SessionBundle
from utils.common.wexinasyncapi import WeixinAsyncApi
from setting import settings
from utils.wechat.oauth import get_oauth_code

from utils.tool.url_tool import make_url

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
_base = type("_base", (web.RequestHandler,), obDict)


# 与基础服务交互时用来标记请求来源
APP_ID = ObjectDict({
    constant.ENV_QX: '5',
    constant.ENV_PLATFORM: '6',
    constant.ENV_HELP: '7'
})


class BaseHandler(_base):

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.json_args = None
        self.params = self._get_params()
        self._log_info = None
        self.start_time = time.time()
        self.app_id = APP_ID.get(options.env)
        self.in_wechat, self.client_type = self._depend_wechat()

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
    def redis(self):
        return self.application.redis

    @property
    def log_info(self):
        if self._log_info and isinstance(self._log_info, dict):
            return self._log_info
        return None

    @log_info.setter
    def log_info(self, value):
        assert isinstance(value,dict )
        self._log_info = dict(value)

    def _get_params(self):
        """
        To get all GET or POST arguments from http request
        """
        params = ObjectDict(self.request.arguments, default="")
        for key in dict(params):
            if isinstance(params[key], list) and len(params[key]):
                params[key] = params[key][0]
        return params

    def _prepare_weixin_auth(self):
        """
        所有url访问的前处理
        1. 向仟寻授权，创建仟寻号下微信用户
        2. 向企业号静默授权，创建企业号下微信用户
        3. 绑定sysuser和user_wx_user关系
        """
        if self.request.method.lower() == "get" and self.in_wechat:

            # 手动获取 m 值，再在 make_url 中显式赋值，因为 make_url 会删除 m 字段
            method = self.params.get("m", None)
            query = dict(host=self.request.host,
                         protocol=self.request.protocol,
                         escape=["code"])
            if method:
                query.update(m=method)

            redirect_url = make_url(self.request.uri.split("?")[0],
                                    self.params, **query)

            # 向聚合号授权并登录
            # 若没有 user_user,则创建 user_user 帐号
            if not self.current_user.qxuser.get("id"):
                # 跳转到仟寻公众号地址，获得code
                redirect_url = make_url(
                    constant.QX_HOST + constant.WXOAUTH_URL, redirect_url)
                qx_wechat = yield self.wechat_ps.get_wechat(
                    conds={"id": settings["qx_wechat_id"]})
                self.wechat_oauth_ps.get_oauth_code(
                    self, redirect_url, qx_wechat, oauth_type="userinfo")

            # 向企业号静默授权，并创建企业微信用户
            elif not self.current_user.wxuser.get("id") and \
                self.current_user.wechat.type == constant.WECHAT_TYPE_SERVICE:
                wechat = self.current_user.wechat
                self.wechat_oauth_ps.get_oauth_code(
                    self, redirect_url, wechat, oauth_type="base")

            # 绑定企业微信用户和 sysuser
            if (not self.current_user.wxuser.get("sysuser_id") or
                not self.current_user.qxuser.get("sysuser_id")) and \
                    self.current_user.sysuser.get("id"):

                user_user_id = self.current_user.sysuser.get("id")

                # 将 user_user.id 与qxuser、wxuser 绑定
                yield self.user_ps.binding_user(
                    self, user_user_id, self.current_user.wxuser,
                    self.current_user.qxuser)

    def _prepare_json_args(self):
        self.json_args = None
        headers = self.request.headers
        try:
            if ("application/json" in headers.get("Content-Type", "") and
                    self.request.body):
                self.json_args = ujson.loads(self.request.body)
        except Exception as e:
            self.logger.error(e)




    # TODO: 暂时注释，因为此项目不是 hr，并不是所有的交互都是 JSON API
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
        wechat_signature = str(self.params.get("wechat_signature", ""))
        conds = ObjectDict({'signature': wechat_signature})
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
                "theme": [
                    theme.get("background_color"),
                    theme.get("title_color"),
                    theme.get("button_color"),
                    theme.get("other_color")
                ]
            })
        else:
            # TODO 暂时做初始化
            company.update({
                "theme": None
            })

        raise gen.Return(company)

    # Get_current_user may not be a coroutine
    # So don't use it
    # We can set the current_user in prepare() by asynchronous operations
    def prepare(self):
        self._make_json_args()
        self._prepare_weixin_auth()

    # def get_current_user(self, oauth=True):
    #     session = ObjectDict()
    #
    #     # session_id
    #     if self.get_secure_cookie(constant.COOKIE_SESSIONID):
    #         session_id = self.get_secure_cookie(constant.COOKIE_SESSIONID)
    #         if self.redis.exists(session_id):
    #             session = yield self.get_current_session(session_id=session_id)
    #             raise gen.Return(session)
    #
    #     wechat = yield self._get_current_wechat()
    #     if not wechat:
    #         raise gen.Return(session)
    #     session_id = self._create_new_session_id(wechat_id=wechat.id)
    #     session = yield self.create_current_session(session_id=session_id, wechat=wechat, oauth=oauth)
    #     self.set_secure_cookie(constant.COOKIE_SESSIONID, session_id)
    #     raise gen.Return(session)

    def _create_new_session_id(self, wechat_id):
        while True:
            session_id = sha1('%s%s' % (os.urandom(16), time.time())).hexdigest() + "_" + wechat_id
            record = yield self.redis.exists(session_id)
            if record:
                continue
            else:
                raise gen.Return(session_id)

    @gen.coroutine
    def get_current_session(self, session_id):
        session = yield self.session_ps.get_session_by_session_id(session_id)
        raise gen.Return(session)

    @gen.coroutine
    def create_current_session(self, session_id=None, wechat=None, oauth=True):
        # qxuser
        qxuser = yield self._get_current_moseeker_wxuser(oauth=oauth)
        # wxuser
        wxuser = yield self._get_current_wxuser(wechat=wechat, qxuser=qxuser, oauth=oauth)
        # user
        user = yield self._get_current_user_user(user_id=wxuser.sysuser_id)
        # company
        company = yield self._get_current_company(company_id=wechat.company_id)
        # employee
        employee = yield self._get_current_employee(wxuser_id=wxuser.id, company_id=company.id)
        # recom
        if "recom" in self.params:
            recom = yield self._get_current_recom(openid=self.params.recom)
        else:
            recom = None

        session = SessionBundle(session_id=session_id)
        session.load_data(wxuser=wxuser,
                          qxuser=qxuser,
                          employee=employee,
                          sysuser=user,
                          recom=recom,
                          company=company,
                          wechat=wechat)
        self.redis.set(session._session_id, session, ttl=60*60*2)
        raise gen.Return(session)

    @gen.coroutine
    def _get_current_user_user(self, user_id=None):
        user = SysUser(id=user_id)
        user.fetch_from_db()
        raise gen.Return(user)

    @gen.coroutine
    def _get_current_recom(self, openid=None):
        recom = Recom(openid=openid)
        recom.fetch_from_db()
        raise gen.Return(recom)

    @gen.coroutine
    def _get_current_employee(self, wxuser_id=None, company_id=None):
        if options.env == constant.ENV_QX:
            raise gen.Return(None)

        employee = Employee(wxuser_id=wxuser_id, company_id=company_id)

        employee.fetch_from_db()
        raise gen.Return(employee)

    @gen.coroutine
    def _get_current_wechat(self, is_qx=False):
        # 如果当前环境是 QX， 使用另一方法获取
        if options.env == constant.ENV_QX or is_qx:
            signature = settings["qx_signature"]
        else:
            signature = self.params.get("wechat_signature", None)
            if not signature:
                self.logger.error("wechat_signature does not exist!")
                return

        wechat = Wechat(signature=signature)
        wechat.fetch_from_db()

        jsapi = JsApi(
            jsapi_ticket=wechat.jsapi_ticket,
            url=self.request.protocol + '://' +
                self.request.host + self.request.uri)

        wechat.jsapi = jsapi
        raise gen.Return(wechat)

    @gen.coroutine
    def _get_current_moseeker_wechat(self):
        ret = yield self._get_current_wechat(is_qx=True)
        raise gen.Return(ret)

    @gen.coroutine
    def _get_current_moseeker_wxuser(self, oauth):
        """
        通过用户授权创建仟寻公众号用户
        :param oauth 是否需要微信授权
        :return:
        """
        # linkedin 也有授权，当是linkedin的code时候，直接返回''
        response = {}
        if not oauth:
            raise gen.Return(response)

        # code不存在，直接返回一个‘’
        if not self.params.code:
            raise gen.Return(response)

        wechat = yield self._get_current_moseeker_wechat()
        httpclient = WeixinAsyncApi(access_token=wechat.access_token,
                                    appid=wechat.appid,
                                    appsecret=wechat.secret)
        response = yield httpclient.get_userinfo_by_code(self.params.code, wechat)

        self.params.pop("code", None)

        response = ObjectDict(ujson.loads(response.body), default="")
        # 创建仟寻公众号下微信用户，创建sysuser用户，登录，并将仟寻用户信息写入session
        if response.get("unionid"):
            yield self.user_wx_user_ds.create_user(self, response, wechat.id)
        else:
            raise gen.Return(response)

        raise gen.Return(response)

    @gen.coroutine
    def _get_current_wxuser(self, wechat, qxuser, oauth):
        """
        :param wechat:
        :param oauth: 不需要授权微信
        :return:
        """

        # linkedin 也有授权，当是 linkedin 的 code 时候，直接返回 ''
        if not oauth:
            raise gen.Return('')

        # code不存在，直接返回一个‘’
        if not self.params.code:
            raise gen.Return('')

        # 第三方平台授权oauth
        component_access_token = None
        # 1：第三方授权 0：第三方未授权
        if wechat.third_oauth == 1:
            component_access_token = self.redis.get('component_access_token')
            if component_access_token:
                component_access_token = ujson.loads(component_access_token).get('component_access_token')

        httpclient = WeixinAsyncApi(
            appid=wechat.appid,
            appsecret=wechat.secret,
            component_access_token=component_access_token)
        response = yield httpclient.get_openid_by_code(
            self.params.code, wechat)

        self.params.pop("code", None)

        response = ObjectDict(ujson.loads(response.body), default="")

        # 由于企业静默授权，只能获取openid。所以用户其他信息，由仟寻公众号下基础信息补充
        result = ObjectDict({
            "openid":     response.openid,
            "nickname":   qxuser.get("nickname"),
            "sex":        qxuser.get("sex", 0),
            "city":       qxuser.get("city"),
            "country":    qxuser.get("country"),
            "province":   qxuser.get("province"),
            "language":   qxuser.get("language"),
            "headimgurl": qxuser.get("headimgurl"),
            "unionid":    qxuser.get("unionid")
        })

        if response.openid:
            # 创建及更新，保证最新的oauth取到的用户信息都能存储上
            yield self.session_ps.create_or_update_wxuser(self, result, wechat.id)
        else:
            raise gen.Return("")

        raise gen.Return(result.openid)

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
        pass

    @gen.coroutine
    def put(self):

        """
        PUT请求父类，用户update类请求
        :return:
        """
        pass

    @gen.coroutine
    def delete(self):

        """
        DELETE请求父类
        :return:
        """
        pass

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

        """
        错误页
        :param status_code: http_status
        :param kwargs:
        :return:

        usage：
            403（用户未被授权请求） Forbidden: Request failed because user does not have authorization to access a specific resource
            404（资源不存在）Resource not found
            500（服务器错误） Internal Server Error: Something went wrong on the server, check status site and/or report the issue
        """

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

        # remote debug mode
        if self.settings.get('remote_debug', False) is True:
            template_string = super(BaseHandler, self).render_string(template_name, **kwargs)
            post_url = urljoin(self.settings.get('remote_debug_ip'), template_name)
            http_client = tornado.httpclient.HTTPClient()
            r = http_client.fetch(post_url, method="POST", body=template_string)
            self.write(r.body)
            self.finish()
            return

        super(BaseHandler, self).render(template_name, **kwargs)
        return

    # def send_json(self, chunk, status_code=200):
    #     self.log_info = {"res_type": "json"}
    #     chunk = ujson.encode(chunk)
    #     self.set_header("Content-Type", "application/json; charset=UTF-8")
    #     self.set_status(status_code)
    #     self.write(chunk)
    #     return

    def send_json(self, json_dict, code=200, use_encoder=True,
                  additional_dump=False):
        """
        传递 JSON 到前端
        :param json_dict: dict 格式的 JSON 内容
        :param code: HTTP code
        :param use_encoder: 是否使用 Tornado 的 json_encode 方法做字符串 escape
        :param additional_dump:
         当前端是 vue.js 渲染的时候 additional_dump 需要设置为 True,
         由 vue.js 将 JSON 字符串 load 成 JS 对象
        """
        json_string = ""
        if use_encoder:
            json_string = tornado.escape.json_encode(json_dict)
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.set_status(code)
        if additional_dump:
            json_string = ujson.dumps(json_string)
        self.write(json_string)

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

        if req_params and req_params.get('password', 0) != 0:
            req_params['password'] = 'xxxxxx'

        log_info_common = ObjectDict(
            elapsed_time="%.4f" % (time.time() - self.start_time),
            product=self.env,
            type_wechat=self.in_wechat,
            type_mobile=self.client_type,
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

    def _depend_wechat(self):
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
