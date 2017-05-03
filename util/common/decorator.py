# coding=utf-8

import re
import functools
import hashlib
import traceback
from abc import ABCMeta, abstractmethod
from urllib.parse import urlencode

from tornado import gen
from tornado.locks import Semaphore
from tornado.web import MissingArgumentError

import conf.common as const
import conf.message as msg
import conf.path as path
import conf.qx as qx_const
from util.common import ObjectDict
from util.common.cache import BaseRedis
from util.common.cipher import encode_id
from util.tool.dict_tool import sub_dict
from util.tool.str_tool import to_hex, to_str


def handle_response(func):
    @functools.wraps(func)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):

        try:
            yield func(self, *args, **kwargs)
        except Exception as e:
            self.logger.error(traceback.format_exc())
            if self.request.headers.get("Content-Type", "").startswith("application/json") \
                or self.request.method in ("PUT", "POST", "DELETE"):
                self.send_json_error()
            else:
                self.write_error(500)
                return
    return wrapper


base_cache = BaseRedis()
sem = Semaphore(1)

def cache(prefix=None, key=None, ttl=60, hash=True, lock=True, separator=":"):
    """
    cache装饰器

    :param prefix: 指定prefix
    :param key: 指定key
    :param ttl: ttl (s)
    :param hash: 是否需要hash
    :param lock: -
    :param separator: key 分隔符
    :return:
    """
    key_ = key
    ttl_ = ttl
    hash_ = hash
    lock_ = lock
    prefix_ = prefix
    separator_ = separator

    def cache_inner(func):

        key, ttl, hash, lock, prefix, separator = key_, ttl_, hash_, lock_, prefix_, separator_

        prefix = prefix if prefix else "{0}:{1}".format(func.__module__.split(".")[-1], func.__name__)

        @functools.wraps(func)
        @gen.coroutine
        def func_wrapper(*args, **kwargs):

            if lock:
                yield sem.acquire()

            try:
                if not key:

                    redis_key = ""

                    if args and len(args) > 1:
                        if isinstance(args[1], dict):
                            redis_key = separator.join([str(_) for _ in list(args[1].values())])
                        else:
                            redis_key = separator.join([str(_) for _ in args[1:]])
                    if kwargs:
                        spliter = separator if redis_key else ""
                        redis_key = redis_key + spliter + separator.join([str(_) for _ in list(kwargs.values())])
                else:
                    redis_key = key

                if hash:
                    redis_key = hashlib.md5(redis_key.encode("utf-8")).hexdigest()

                redis_key = "{prefix}{separator}{redis_key}".format(prefix=prefix, separator=separator,
                                                                    redis_key=redis_key)

                if base_cache.exists(redis_key):
                    cache_data = base_cache.get(redis_key)
                else:
                    cache_data = yield func(*args, **kwargs)
                    if cache_data is not None:
                        base_cache.set(redis_key, cache_data, ttl)

                raise gen.Return(cache_data)

            finally:
                if lock:
                    sem.release()

        return func_wrapper

    return cache_inner


def check_signature(func):
    """如果当前环境是企业号但是url query 没有 wechat_signature, 返回 404

    此装饰器用来装饰 tornado.web.RequestHandler 异步方法，
    如：prepare
    """

    @functools.wraps(func)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):
        if self.is_platform:
            key = "wechat_signature"
            try:
                self.get_argument(key, strip=True)
            except MissingArgumentError:
                self.write_error(http_code=404)
                return

        yield func(self, *args, **kwargs)

    return wrapper


def check_employee(func):
    """前置判断当前用户是否是员工

    如果是员工，这正常进入 handler 的对应方法，如果不是员工，跳转到认证员工页面
    用于我要推荐
    """
    @functools.wraps(func)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):
        if self.params.recomlist and not self.current_user.employee:
            # 如果从我要推荐点进来，但当前用户不是员工
            # 跳转到员工绑定页面
            self.params.pop("recomlist", None)
            self.redirect(self.make_url(path.EMPLOYEE_VERIFY, self.params))
            return
        else:
            yield func(self, *args, **kwargs)

    return wrapper


def check_and_apply_profile(func):
    """前置判断当前用户是否有 profile
    如果没有， 跳转到新建 profile 页面
    如果有，将 profile 放到 current_user 下"""

    @functools.wraps(func)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):
        user_id = self.current_user.sysuser.id
        has_profile, profile = yield self.profile_ps.has_profile(user_id)
        if has_profile:
            self.current_user['profile'] = profile
            self.logger.debug(profile)
            yield func(self, *args, **kwargs)
        else:
            # render new profile entry 页面
            self.logger.debug(self.request.uri)
            self.logger.warn(
                "userid:%s has no profile, redirect to profile_new" %
                self.current_user.sysuser.id)

            # 跳转模版需要的参数初始值
            redirect_params = {
                "use_email": False,
                "goto_custom_url": '',
            }

            # 如果是申请中跳转到这个页面，需要做详细检查
            self.logger.warn(self.request.uri.split('?')[0])
            self.logger.warn(self.params)

            if self.request.uri.split('?')[0] == path.APPLICATION and \
                self.params.pid and self.params.pid.isdigit():

                pid = int(self.params.pid)
                position = yield self.position_ps.get_position(pid)

                self.logger.warn(position)

                # 判断是否可以接受 email 投递
                redirect_params.update(
                    use_email=(position.email_resume_conf == const.OLD_YES))

                # 判断是否是自定义职位
                if position.app_cv_config_id:
                    redirect_params.update(goto_custom_url=self.make_url(
                        path.PROFILE_CUSTOM_CV,
                        sub_dict(self.params, ['pid', 'wechat_signature'])))
            else:
                # 从侧边栏直接进入，允许使用 email 创建 profile
                redirect_params.update(use_email=True)

            # ========== LINKEDIN OAUTH ==============
            # 拼装 linkedin oauth 路由
            redirect_uri = self.make_url(path.RESUME_LINKEDIN,
                                    recom=self.params.recom,
                                    pid=self.params.pid,
                                    wechat_signature=self.current_user.wechat.signature)

            linkedin_url = self.make_url(path.LINKEDIN_AUTH, params=ObjectDict(
                response_type="code",
                client_id=self.settings.linkedin_client_id,
                scope="r_basicprofile r_emailaddress",
                redirect_uri=redirect_uri
            ))
            # 由于 make_url 会过滤 state，但 linkedin 必须传 state，故此处手动添加
            linkedin_url = "{}&state={}".format(linkedin_url, encode_id(self.current_user.sysuser.id))

            self.logger.debug("linkedin:{}".format(redirect_uri))
            self.logger.debug("linkedin 2:{}".format(linkedin_url))
            redirect_params.update(linkedin_url=linkedin_url)
            # ========== LINKEDIN OAUTH ==============

            self.logger.warn(redirect_params)

            self.render(template_name='refer/neo_weixin/sysuser/importresume.html',
                        **redirect_params)

    return wrapper


def check_sub_company(func):
    """
    Check request sub_company data or not.
    :param func:
    :return: Http404 or set sub_company in params
    """

    @functools.wraps(func)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):
        if self.params.did and self.params.did != str(self.current_user.company.id):
            sub_company = yield self.team_ps.get_sub_company(self.params.did)
            if not sub_company or \
                    sub_company.parent_id != self.current_user.company.id:
                self.write_error(404)
                return
            else:
                self.logger.debug(
                    'Sub_company: {}'.format(sub_company))
                self.params.sub_company = sub_company

        yield func(self, *args, **kwargs)

    return wrapper


def authenticated(func):
    """
    判断用户是否登录
    若在非微信环境（即手机浏览器等）用户未登录，
    则跳转到配置到 setting 的登录 url。`login url <RequestHandler.get_login_url>`
    若在企业号的服务号环境，则进行静默授权
    """

    @functools.wraps(func)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):
        if self.current_user.sysuser.id and self.in_wechat:
            if self._authable(self.current_user.wechat.type) and not self.current_user.wxuser \
                and self.request.method in ("GET", "HEAD") \
                and not self.request.uri.startswith("/m/api/"):
                # 该企业号是服务号，静默授权
                # api 类接口，不适合做302静默授权，微信服务器不会跳转
                self._oauth_service.wechat = self.current_user.wechat
                self._oauth_service.state = to_hex(self.current_user.qxuser.unionid)
                url = self._oauth_service.get_oauth_code_base_url()
                self.redirect(url)
                return

        elif not self.current_user.sysuser.id:
            if self.request.method in ("GET", "HEAD"):
                redirect_url = self.make_url(path.USER_LOGIN, self.params, escape=['next_url'])
                redirect_url += "&" + urlencode(
                    dict(next_url=self.fullurl))
                self.redirect(redirect_url)
                return
            else:
                self.send_json_error(message=msg.NOT_AUTHORIZED)
                return

        yield func(self, *args, **kwargs)

    return wrapper

def verified_mobile_oneself(func):

    """重要的操作前，如修改密码，修改邮箱等，需要先用手机验证是否是本人操作
    方法：
        1.获得 cookie 中的验证码 code
        2.获取 url 中的加密 code 值
        3.两者是否相等，若相等，则已经验证是本人操作；若不相等，则跳转到验证手机号页面
    """

    @functools.wraps(func)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):
        mobile_code = self.get_secure_cookie(const.COOKIE_MOBILE_CODE)
        url_code = self.params._mc

        if mobile_code is not None and url_code is not None \
            and encode_id(int(mobile_code), 8) == url_code:
            yield func(self, *args, **kwargs)

        else:
            if self.request.method in ("GET", "HEAD"):
                redirect_url = self.make_url(path.MOBILE_VERIFY, params=self.params, escape=['next_url'])

                redirect_url += "&" + urlencode(
                    dict(next_url=self.fullurl))
                self.redirect(redirect_url)
                return
            else:
                self.send_json_error(message=msg.MOBILE_VERIFY)

    return wrapper

def gamma_welcome(func):

    """
    聚合号 gamma 的欢迎页，对于 C 端用户不同性别展现不同的皮肤
    :param func:
    :return:
    """

    @functools.wraps(func)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):

        search_keywords = self.get_secure_cookie(qx_const.COOKIE_WELCOME_SEARCH)

        self.logger.debug("gamma_welcome search_keywords: {}".format(search_keywords))
        self.logger.debug("gamma_welcome self.params: {}".format(self.params))
        self.logger.debug("gamma_welcome self.params.fr: {}".format(self.params.fr))
        self.logger.debug("gamma_welcome uri:{}".format(self.request.uri))
        self.logger.debug("gamma_welcome match:{}".format(re.match(r"^\/position$", self.request.uri)))

        if not search_keywords and self.params.fr != "recruit" \
            and re.match(r"^\/position$", self.request.uri):
            gender = "unkonwn"
            if self.current_user.qxuser.sex == 1:
                gender = "male"
            elif self.current_user.qxuser.sex == 2:
                gender = "female"

            self.logger.debug("gamma_welcome gender: {}".format(gender))
            self.render_page(template_name='qx/home/welcome.html',
                        data={"gender": gender})
            return

        yield func(self, *args, **kwargs)

    return wrapper

# 检查新JD状态, 如果不是启用状态, 当前业务规则:
# 1. JD --> 跳老页面
# 2. Company --> 跳老页面
# 3. TeamIndex --> 404
# 4. TeamDetail --> 404
class BaseNewJDStatusChecker(metaclass=ABCMeta):

    def __init__(self):
        self._handler = None

    def __call__(self, func):
        @functools.wraps(func)
        @gen.coroutine
        def wrapper(handler, *args, **kwargs):
            self._handler = handler
            # 新JD开启状态
            is_newjs_status_on = handler.current_user.company.conf_newjd_status == const.NEWJD_STATUS_ON
            # 预览状态
            is_preview = handler.current_user.company.conf_newjd_status == const.NEWJD_STATUS_WAITING \
                         and handler.params.preview != None
            if not (is_newjs_status_on or is_preview):
                self.fail_action(*args, **kwargs)
                return

            handler.logger.debug('NewJD status check successful: {}'.format(handler.current_user.wechat.id))
            yield func(handler, *args, **kwargs)

        return wrapper

    @abstractmethod
    def fail_action(self, *args, **kwargs):
        raise NotImplemented


class NewJDStatusChecker404(BaseNewJDStatusChecker):
    """ JD status不对应, 直接404 """

    def fail_action(self, *args, **kwargs):
        handler = self._handler
        handler.logger.debug(
            'NewJD status check fail, uri: {}, wechat_id: {}'.format(handler.request.uri,
                                                                     handler.current_user.wechat.id))
        handler.write_error(404)
