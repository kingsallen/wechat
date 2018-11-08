# coding=utf-8
import json
import functools
import hashlib
import re
import traceback
from abc import ABCMeta, abstractmethod
import time
from urllib.parse import urlencode

from tornado import gen
from tornado.locks import Semaphore
from tornado.web import MissingArgumentError

import conf.common as const
import conf.message as msg
import conf.path as path
import conf.qx as qx_const
from globals import logger
from util.common import ObjectDict
from util.common.cache import BaseRedis
from util.common.cipher import encode_id
from util.tool.dict_tool import sub_dict
from util.tool.json_tool import json_dumps
from util.tool.str_tool import to_hex


def handle_response(func):
    @functools.wraps(func)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):

        try:
            yield func(self, *args, **kwargs)
        except Exception as e:
            user_id = 0
            if self.current_user.sysuser:
                user_id = self.current_user.sysuser.id
            error_log_content = {'user_id': user_id, 'message': traceback.format_exc()}

            self.logger.error(json_dumps(error_log_content))

            if self.request.headers.get("Content-Type", "").startswith("application/json") \
                or self.request.method in ("PUT", "POST", "DELETE"):
                self.send_json_error()
            else:
                self.write_error(500, message=getattr(e, "message", None))
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

        prefix = prefix if prefix else "{0}:{1}".format(func.__module__.split(".")[-1], func.__qualname__)

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

                cache_data = None
                try:
                    cache_data = base_cache.get(redis_key)
                except Exception as e:
                    logger.error(e)

                if cache_data is None:
                    cache_data = yield func(*args, **kwargs)
                    if cache_data is not None:
                        try:
                            base_cache.set(redis_key, cache_data, ttl)
                        except Exception as e:
                            logger.error(e)

                raise gen.Return(cache_data)

            finally:
                if lock:
                    sem.release()

        return func_wrapper

    return cache_inner


def common_handler(cls):
    """标记 common handler"""
    cls.is_common = True
    return cls


def check_signature(func):
    """如果当前环境是企业号但是url query 没有 wechat_signature, 返回 404

    此装饰器用来装饰 tornado.web.RequestHandler 异步方法，
    如：prepare
    """

    @functools.wraps(func)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):
        is_common = False
        if hasattr(self, 'is_common'):
            is_common = self.is_common

        if self.is_platform and not is_common:
            key = "wechat_signature"
            try:
                self.get_argument(key, strip=True)
            except MissingArgumentError:
                self.write_error(http_code=404)
                return

        yield func(self, *args, **kwargs)

    return wrapper


def check_employee(func):
    # todo 重构的时候把这个装饰器与check_employee_common合并
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


def check_employee_common(func):
    """前置判断当前用户是否是员工
    如果是员工，这正常进入 handler 的对应方法，如果不是员工，跳转到认证员工页面
    用于常用路由检测
    """

    @functools.wraps(func)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):
        if not self.current_user.employee:
            # 当前用户不是员工，跳转到员工绑定页面
            self.redirect(self.make_url(path.EMPLOYEE_VERIFY, self.params))
            return
        else:
            yield func(self, *args, **kwargs)

    return wrapper


def cover_no_weixin(func):
    """移动端非微信环境下，限制浏览，允许User-Agent中带有moseeker的请求访问，此为测试与开发在非微信移动端的后门"""
    @functools.wraps(func)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):
        if not self.in_wechat and 'moseeker' not in self.request.headers.get('User-Agent'):
            self.render(template_name="adjunct/not-weixin.html")
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
        need_profile_upload = [570004]  # 现在为沙盒的
        user_id = self.current_user.sysuser.id
        has_profile, profile = yield self.profile_ps.has_profile(user_id)
        if has_profile:
            self.current_user['profile'] = profile
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
            # 获取最佳东方导入开关
            company = yield self.company_ps.get_company({'id': self.current_user.wechat.company_id}, need_conf=True)
            importer = ObjectDict(profile_import_51job=True,
                                  profile_import_zhilian=True,
                                  profile_import_liepin=True,
                                  profile_import_linkedin=True,
                                  profile_import_maimai=False,
                                  profile_import_veryeast=False,
                                  resume_upload=False)
            if company.conf_veryeast_switch == 1:
                importer.update(profile_import_veryeast=True)
            if company.id in need_profile_upload:
                importer.update(resume_upload=True)

            # 如果是申请中跳转到这个页面，需要做详细检查
            current_path = self.request.uri.split('?')[0]
            paths_for_application = [path.APPLICATION, path.PROFILE_PREVIEW]

            self.logger.warn(current_path)
            self.logger.warn(self.params)

            if (current_path in paths_for_application and
                    self.params.pid and self.params.pid.isdigit()):

                pid = int(self.params.pid)
                position = yield self.position_ps.get_position(pid, display_locale=self.get_current_locale())

                self.logger.warn(position)

                # 判断是否可以接受 email 投递
                redirect_params.update(
                    use_email=(position.email_resume_conf == const.OLD_YES))

                # 自定义职位
                if position.app_cv_config_id:
                    goto_custom_url = self.make_url(
                        path.PROFILE_CUSTOM_CV,
                        self.params)

                    # 如果是自定义职位，且没有 profile，且是直接投递定制的公司
                    # 直接跳转到自定义填写页面

                    is_direct_apply = yield self.customize_ps.create_direct_apply(
                        position.company_id, position.app_cv_config_id)

                    if is_direct_apply:
                        self.redirect(goto_custom_url)
                        return
                    else:
                        redirect_params.update(goto_custom_url=goto_custom_url)

            else:
                # 从侧边栏直接进入，允许使用 email 创建 profile
                redirect_params.update(use_email=True)

            # ========== MAIMAI OAUTH ===============
            # 拼装脉脉 oauth 路由
            cusdata = "?recom={}&pid={}&wechat_signature={}".format(self.params.recom, self.params.pid,
                                                                    self.current_user.wechat.signature)
            # 加上渠道
            cusdata = "{}&way={}".format(cusdata, const.FROM_MAIMAI)
            # 脉脉cusdata中不允许出现 '&' ，考虑我们公司目前的使用的参数中不会出现 '$$' , 将 '&' 转为 '$$' 使用
            cusdata = cusdata.replace("&", "$$")
            self.logger.info("[maimai_url_cusdata: {}]".format(cusdata))

            cusdata = urlencode(dict(cusdata=cusdata))
            appid = self.settings.maimai_appid
            maimai_url = path.MAIMAI_ACCESSTOKEN.format(appid=appid, cusdata=cusdata)

            # 猎聘用户授权 现场数据缓存
            base_cache.set(
                const.LIEPIN_SCENE_KEY_FMT.format(
                    sysuser_id=self.current_user.sysuser.id
                ),
                json.dumps(dict(
                    recom=self.params.recom,
                    pid=self.params.pid,
                    wechat_signature=self.current_user.wechat.signature
                )),
                const.LIEPIN_SCENE_KEY_TTL
            )

            # 第三方简历导入对接回调地址配置
            redirect_params.update(
                maimai_url=maimai_url,
                liepin_url=path.LIEPIN_ACCESSTOKEN.format(
                    hashlib.sha1(str(self.current_user.sysuser.id).encode('u8')).hexdigest()
                )
            )

            # 是否需要弹出 隐私协议 窗口
            user_id = self.current_user.sysuser.id
            result, data = yield self.privacy_ps.if_privacy_agreement_window(user_id)
            redirect_params.update(
                show_privacy_agreement=data
            )

            redirect_params = {**self.params, **redirect_params}

            self.render(
                template_name='refer/neo_weixin/sysuser_v2/importresume.html',
                **redirect_params,
                importer=importer
            )

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
                sub_company.banner = self.current_user.company.banner  # 子公司采用母公司的banner
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
                and not self.request.uri.startswith("/api/"):
                # 该企业号是服务号，静默授权
                # api 类接口，不适合做302静默授权，微信服务器不会跳转
                self._oauth_service.wechat = self.current_user.wechat
                self._oauth_service.state = to_hex(self.current_user.qxuser.unionid)
                self.logger.info(
                    "静默授权：state:{}-----unionid:{}".format(self._oauth_service.state, self.current_user.qxuser.unionid))
                url = self._oauth_service.get_oauth_code_base_url()
                self.redirect(url)
                return

        elif not self.current_user.sysuser.id:
            if self.request.method in ("GET", "HEAD") and not self.request.uri.startswith("/api/"):
                redirect_url = self.make_url(path.USER_LOGIN, self.params, escape=['next_url'])

                if redirect_url.find('?') == -1:
                    redirect_url += '?'
                else:
                    # 带有query字符串
                    redirect_url += '&'

                redirect_url += urlencode(
                    dict(next_url=self.fullurl()))
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
                    dict(next_url=self.fullurl()))
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

        if not search_keywords and self.params.fr != "recruit" and not self.params.fr_wel \
            and re.match(r"^\/position[\?]?[\w&=%]*$", self.request.uri):
            gender = "unknown"
            if self.current_user.qxuser.sex == 1:
                gender = "male"
            elif self.current_user.qxuser.sex == 2:
                gender = "female"

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
            handler.flag_should_display_newjd = self.should_display_newjd(handler)
            if self.should_display_newjd(handler):
                yield func(handler, *args, **kwargs)
            else:
                yield self.fail_action(func, *args, **kwargs)

        return wrapper

    @staticmethod
    def should_display_newjd(handler):
        is_newjd_status_on = handler.current_user.company.conf_newjd_status == const.NEWJD_STATUS_ON
        # 预览状态
        is_preview = (handler.current_user.company.conf_newjd_status == const.NEWJD_STATUS_WAITING
                      and handler.params.preview != None)
        return is_newjd_status_on or is_preview

    @abstractmethod
    def fail_action(self, func, *args, **kwargs):
        raise NotImplemented


class NewJDStatusChecker404(BaseNewJDStatusChecker):
    """ JD status不对应, 直接404 """

    @gen.coroutine
    def fail_action(self, func, *args, **kwargs):
        handler = self._handler
        handler.write_error(404)


class NewJDStatusCheckerAddFlag(BaseNewJDStatusChecker):
    """检查一下, 放置一个标志位, 仍然执行原func"""

    @gen.coroutine
    def fail_action(self, func, *args, **kwargs):
        yield func(self._handler, *args, **kwargs)


def log_time(func):
    @functools.wraps(func)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):
        start = time.time()
        r = yield func(self, *args, **kwargs)
        end = time.time()
        c = {
            "for": "[hb_debug]",
            "func_name": func.__qualname__,
            "time": (end - start) * 1000
        }
        self.logger.info(json_dumps(c))
        return r

    return wrapper
