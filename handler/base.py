# coding=utf-8

# Copyright 2016 MoSeeker

import glob
import importlib
import os
import re
import socket
import time
import ujson
from hashlib import sha1
from urllib.parse import urljoin

import tornado.escape
import tornado.httpclient
from tornado import gen, web
from app import logger
from oauth.wechat import WeChatOauth2Service, WeChatOauthError
from util.common import ObjectDict
from util.common.decorator import check_signature
from util.session.session import JsApi, Wechat, WxUser, Recom, Employee, SysUser
from util.tool.json_tool import encode_json_dumps
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


class NoSignatureError(Exception):
    pass


class BaseHandler(MetaBaseHandler):
    """
    Handler 基类

    不要使用（创建）get_current_user()
    get_current_user() 不能为异步方法，而 parpare() 可以
    self.current_user 将在 prepare() 中以 self.current_user = XXX 的形式创建

    Refer to:
    http://www.tornadoweb.org/en/stable/web.html#other
    """

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

        # 全部 arguments
        self.params = self._get_params()
        # api 使用， json arguments
        self.json_args = self._get_json_args()

        # 记录初始化的时间
        self._start_time = time.time()

        # 保存是否在微信环境， 微信客户端类型
        self.in_wechat, self.client_type = self._depend_wechat()

        # 日志信息
        self._log_info = None

        # 构建 session 过程中会缓存一份当前公众号信息
        self._wechat = None
        self._qx_wechat = None
        self._unionid = None
        self._wxuser = None

        # 处理 oauth 的 service
        self._oauth_service = WeChatOauth2Service(self, self.fullurl)

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
    def is_platform(self):
        return self.env == self.constant.ENV_PLATFORM

    @property
    def is_qx(self):
        return self.env == self.constant.ENV_QX

    @property
    def is_help(self):
        return self.env == self.constant.ENV_HELP

    @property
    def app_id(self):
        """appid for infra"""
        bundle = {
            self.constant.ENV_QX:       '5',
            self.constant.ENV_PLATFORM: '6',
            self.constant.ENV_HELP:     '7'
        }
        return bundle[self.env]

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
    def wx_constant(self):
        return self.application.wx_constant

    @property
    def redis(self):
        return self.application.redis

    @property
    def log_info(self):
        return self._log_info

    @property
    def fullurl(self):
        return (self.request.protocol + "://" +
                self.request.host + self.request.uri)

    @log_info.setter
    def log_info(self, value):
        self._log_info = dict(value)

    # PUBLIC API
    @check_signature
    @gen.coroutine
    def prepare(self):
        # 构建 session 之前先缓存一份 wechat
        self._wechat = yield self._get_current_wechat()
        self._qx_wechat = yield self._get_qx_wechat()

        # 如果有 code，说明刚刚从微信 oauth 回来
        code = self.params.get("code")
        state = self.params.get("state")

        if code:  #用户同意授权
            if state == 'O':  #来自 qx 的授权, 获得 userinfo
                userinfo = yield self._get_user_info(code)
                yield self._handle_user_info(userinfo)
            else:  #来自企业号的静默授权
                self._unionid = state
                openid = yield self._get_user_openid(code)
                self._wxuser = yield self._handle_ent_openid(openid, self._unionid)
        if state and not code:  #用户拒绝授权
            #TODO 拒绝授权用户，是否让其继续操作。or return
            pass

        # 构造并拼装 session
        yield self._fetch_session()

        # 内存优化
        self._wechat = None
        self._qx_wechat = None
        self._unionid = None
        self._wxuser = None

    # PROTECTED
    @gen.coroutine
    def _handle_user_info(self, userinfo):
        """
        根据 unionid 创建 user_user 如果存在则不创建， 返回 user_id
        创建 聚合号 wxuser，绑定刚刚创建的 user_id
        静默授权企业号, state 为 unionid

        userinfo 结构：
        ObjectDict(
        "openid":" OPENID",
        "nickname": NICKNAME,
        "sex":"1",
        "province":"PROVINCE"
        "city":"CITY",
        "country":"COUNTRY",
        "headimgurl":    "http://wx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx",
        "privilege":[
                        "PRIVILEGE1"
                        "PRIVILEGE2"
                    ],
        "unionid": "o6_bmasdasdsad6_2sgVt7hMZOPfL"
        )
        """

        unionid = userinfo.unionid
        # TODO create_user_user create_user_wx_user_by_userinfo
        user_id = yield self.user_ps.create_user_user(userinfo)
        yield self.user_ps.create_user_wx_user_by_userinfo(user_id, userinfo)
        if self.is_platform:
            self._oauth_service.wechat = self._wechat
            self._oauth_service.status = unionid
            # TODO 静默授权？
            self._oauth_service.get_oauth_code_base()

        # TODO 删了？
        # self._oauth_service.get_oauth_code_base()

    @gen.coroutine
    def _handle_ent_openid(self, openid, unionid):
        """根据企业号 openid 和 unionid 创建企业号微信用户"""
        wxuser = None
        user = self.user_ps.get_user_by_union_id(unionid)
        unionid = user.unionid
        if self.is_platform:
            # TODO create_user_wx_user_ent
            wxuser = yield self.user_ps.create_user_wx_user_ent(
                openid, unionid, self._wechat.id)
        raise gen.Return(wxuser)

    def _get_params(self):
        """To get all GET or POST arguments from http request
        """
        params = ObjectDict(self.request.arguments)
        for key in params:
            if isinstance(params[key], list) and params[key]:
                params[to_str(key)] = to_str(params[key][0])
        return params

    def _get_json_args(self):
        json_args = {}

        content_type = self.request.headers.get("Content-Type")
        if content_type and "application/json" in content_type and self.request.body:
            json_args = ujson.loads(self.request.body)

        return ObjectDict(json_args)

    @gen.coroutine
    def _get_current_wechat(self, qx=False):
        if qx:
            signature = self.settings['qx_signature']
        else:
            if self.is_platform:
                signature = self.params['wechat_signature']
            elif self.is_qx:
                signature = self.settings['qx_signature']
            elif self.is_help:
                signature = self.settings['helper_signature']
            else:
                self.logger.error("wechat_signature missing")
                raise NoSignatureError()

        wechat = yield Wechat(signature=signature).fetch_from_db()
        wechat.jsapi = JsApi(
            jsapi_ticket=wechat.jsapi_ticket, url=self.fullurl)

        raise gen.Return(wechat)

    @gen.coroutine
    def _get_qx_wechat(self):
        wechat = yield self._get_current_wechat(qx=True)
        raise gen.Return(wechat)

    @gen.coroutine
    def _get_current_company(self, company_id):
        """
        # 获得企业母公司信息
        """
        conds = {'id': company_id}
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
            company.update({"theme": None})

        raise gen.Return(company)

    @gen.coroutine
    def _get_user_info(self, code):
        self._oauth_service.wechat = self._qx_wechat
        try:
            userinfo = yield self._oauth_service.get_userinfo_by_code(code)
            raise gen.Return(userinfo)
        except WeChatOauthError as e:
            self.logger.error(e)

    @gen.coroutine
    def _get_user_openid(self, code):
        self._oauth_service.wechat = self._wechat
        try:
            openid, _ = yield self._oauth_service.get_openid_unionid_by_code(code)
            raise gen.Return(openid)
        except WeChatOauthError as e:
            self.logger.error(e)

    @gen.coroutine
    def _fetch_session(self):
        """尝试获取 session 并创建 current_user，如果获取失败走 oauth 流程"""
        need_oauth = False
        ok = False

        session_id = self.get_secure_cookie(self.constant.COOKIE_SESSIONID)

        if session_id:
            if self.is_platform:
                ok = self._get_session_from_ent(session_id)
                if not ok:
                    ok = yield self._get_session_from_qx(session_id)
            elif self.is_qx:
                ok = yield self._get_session_from_qx(session_id)

            elif self.is_help:
                pass

            need_oauth = not ok

        else:
            need_oauth = True

        if need_oauth:
            if self._unionid and self._wxuser:
                yield self._build_session()
            else:
                self._oauth_service.wechat = self._qx_wechat
                self._oauth_service.get_oauth_code_userinfo()

    @gen.coroutine
    def _build_session(self):
        session = ObjectDict()
        session.wechat = self._wechat
        session.wxuser = self._wxuser

        qxuser = WxUser(unionid=self._unionid, wechat_id=self.settings['qx_wechat_id'])
        session.qxuser = yield qxuser.fetch_from_db()

        session.company = yield self._get_current_company(self._wechat.id)

        user = SysUser(id=qxuser.sysuser_id)
        session.sysuser = yield user.fetch_from_db()

        session_id = self._make_new_session_id()
        self.set_secure_cookie(self.constant.COOKIE_SESSIONID, session_id)
        # TODO REDIS KEY  常量配置
        self.redis.set(
            self.constant.SESSION_USER.format(session_id, self._wechat.id), ujson.dumps(session),
            60 * 60 * 2)

        if self.is_platform:
            employee = Employee(
                wxuser_id=session.wxuser.id, company_id=session.company.id)
            employee.fetch_from_db()
            if employee:
                session.employee = employee

        if 'recom' in self.params:
            recom = Recom(openid=self.params.openid)
            recom.fetch_from_db()
            session.recom = recom

        self.current_user = session

    def _get_session_from_ent(self, session_id):
        """尝试获取 session"""
        if not self.is_platform:
            return False

        # TODO REDIS KEY 常量配置
        key = self.constant.SESSION_USER.format(session_id, self._wechat.id)
        # key = session_id + "_" + self._wechat.id
        value = self.redis.get(key)
        if value:
            # 如果有 value， 返回该 value 作为 self.current_user
            self.current_user = ujson.loads(value)
            return True
        return False

    @gen.coroutine
    def _get_session_from_qx(self, session_id):
        """尝试获取聚合号 session"""
        # TODO REDIS KEY 常量配置
        key = self.constant.SESSION_USER.format(session_id, self.settings['qx_wechat_id'])
        # key = session_id + "_" + self.settings['qx_wechat_id']
        value = self.redis.get(key)
        if value:
            user_id = ujson.loads(value).user.id
            # TODO _refresh_session，或者是_build_session？
            session_qx, session_ent = yield self._refresh_session(user_id)
            if self.is_platform:
                self.current_user = session_ent
            elif self.is_qx:
                self.current_user = session_qx

            raise gen.Return(True)
        raise gen.Return(False)

    def _make_new_session_id(self):
        """创建新的 session_id

        redis 中 session 的 key 的格式为 session_id_<wechat_id>
        创建的 session_id 保证唯一
        session_id 目前本身不做持久化，仅仅保存在 redis 中
        后续是否需要做持久化待讨论
        :return: session_id
        """
        while True:
            _t = time.time()
            _r = os.urandom(16)
            session_id = sha1(_t + _r).hexdigest()
            record = self.redis.exists(session_id + "_*")
            if record:
                continue
            else:
                return session_id

    @gen.coroutine
    def get(self):
        pass

    @gen.coroutine
    def post(self):
        pass

    @gen.coroutine
    def put(self):
        pass

    @gen.coroutine
    def delete(self):
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
        """错误页
        :param status_code: http_status

        usage：
        403（用户未被授权请求） Forbidden: Request failed because user does not have authorization to access a specific resource
        404（资源不存在）      Resource not found
        500（服务器错误）      Internal Server Error: Something went wrong on the server, check status site and/or report the issue
        """

        if status_code == 403:
            self.render('refer/common/info.html', status_code=status_code,
                        css="warning", info="用户未被授权请求")
        elif status_code == 404:
            self.render('common/systemmessage.html', status_code=status_code,
                        message="Ta在地球上消失了")
        else:
            self.render('common/systemmessage.html', status_code=status_code,
                        message="正在努力维护服务器中")

    def render(self, template_name, status_code=200, **kwargs):
        """render 页面"""
        self.log_info = {"res_type": "html"}
        self.set_status(status_code)

        # 前后端联调使用
        if self.settings.get('remote_debug', False) is True:
            template_string = self.render_string(template_name, **kwargs)
            post_url = urljoin(self.settings.get('remote_debug_ip'),
                               template_name)
            http_client = tornado.httpclient.HTTPClient()
            r = http_client.fetch(post_url, method="POST",
                                  body=template_string)
            self.write(r.body)
            self.finish()
            return

        self.render(template_name, **kwargs)
        return

    def send_json(self, json_dict, code=200, use_encoder=True,
                  additional_dump=False):
        """传递 JSON 到前端

        Used for API
        """
        json_string = ""
        if use_encoder:
            json_string = tornado.escape.json_encode(json_dict)
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.set_status(code)
        if additional_dump:
            json_string = ujson.dumps(json_string)
        self.write(json_string)

    @staticmethod
    def _make_render_json(data, status=0, message="", ):
        """制造 render_json 用于渲染模板

        由调用者负责传入数据的格式，此处不做检查
        Used for Render
        """
        render_json = {
            "status": status,
            "message": message,
            "data": data
        }
        return encode_json_dumps(render_json)

    def _get_info_header(self, log_params):
        request = self.request
        req_params = request.arguments

        if req_params and req_params.get('password', 0) != 0:
            req_params['password'] = 'xxxxxx'

        log_info_common = ObjectDict(
            elapsed_time="%.4f" % (time.time() - self._start_time),
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
        """判断用户UA是否为微信客户端
        """
        wechat = self.constant.CLIENT_NON_WECHAT
        mobile = self.constant.CLIENT_TYPE_UNKNOWN

        useragent = self.request.headers.get('User-Agent')
        if "MicroMessenger" in useragent:
            if "iPhone" in useragent:
                mobile = self.constant.CLIENT_TYPE_IOS
            elif "Android" in useragent:
                mobile = self.constant.CLIENT_TYPE_ANDROID
            wechat = self.constant.CLIENT_WECHAT

        return wechat, mobile
