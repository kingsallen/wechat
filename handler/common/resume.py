# coding=utf-8
import hashlib
import json
import urllib.parse
import re

from tornado import gen

import conf.path as path
import conf.message as msg
import conf.common as const
from handler.base import BaseHandler
from handler.metabase import MetaBaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated

from util.tool.str_tool import to_str, match_session_id
from util.tool.url_tool import make_url


class ThirdpartyImportHandler(MetaBaseHandler):
    """
    外部接口导入简历时，当参数需要特殊处理时，先调用该handler处理,
    因为BaseHandler会处理signature，第三方网站回调时可能没有signature，
    因此直接继承MetaBaseHandler
    """

    @handle_response
    @gen.coroutine
    def get(self):
        params = urllib.parse.unquote(self.params.cusdata)
        params = params.replace("$$", "&")  # 脉脉需要我们自己拼接redirect_url放入某个参数中，http链接中不能带&，因此替换成了$$,在这里换回来
        self.logger.info("[maimai_url_params: {}]".format(params))
        way = re.search(r'way=([0-9]*)', params).group(1)

        if int(way) == const.FROM_MAIMAI:
            token = self.params.t
            unionid = self.params.u
            params = '{}&token={}&unionid={}'.format(str(params), token, unionid)
            redirect_url = path.RESUME_MAIMAI.format(self.host, params)
            self.redirect(redirect_url)
        else:
            wechat_signature = re.search(r'signature=(.*?)&', params).group(1)
            data = ObjectDict(
                kind=1,  # // {0: success, 1: failure, 10: email}
                messages=['该网站出现异常，请换个渠道重试'],  # ['hello world', 'abjsldjf']
                button_text=msg.BACK_CN,
                button_link=self.make_url(path.PROFILE_VIEW,
                                          wechat_signature=wechat_signature,
                                          host=self.host),
                jump_link=None  # // 如果有会自动，没有就不自动跳转
            )

            self.render_page(template_name="system/user-info.html",
                             data=data)
            return


class MaimaiImportHandler(BaseHandler):
    """
    脉脉导入
    """

    @handle_response
    @gen.coroutine
    def get(self):
        token = self.params.token
        unionid = self.params.unionid

        if not token and unionid:
            self.write_error(404)
            return

        appid = self.settings.maimai_appid
        user_id = match_session_id(to_str(self.get_secure_cookie(const.COOKIE_SESSIONID)))
        ua = 1 if self.in_wechat else 2
        is_ok, result = yield self.profile_ps.import_profile(10, "", "", user_id, ua, token=token, unionid=unionid,
                                                             appid=appid, version=1.0)
        self.handle_profile(is_ok=is_ok, result=result)

    def handle_profile(self, is_ok, result):

        self.logger.debug("is_ok:{} result:{}".format(is_ok, result))
        if is_ok:
            if self.params.pid:
                next_url = make_url(path.PROFILE_PREVIEW, params=self.params, host=self.host)
            else:
                next_url = make_url(path.PROFILE_VIEW, params=self.params, host=self.host)

            self.redirect(next_url)
            return
        else:
            if result.status == 32008:
                messages = msg.PROFILE_IMPORT_LIMIT
            else:
                messages = result.message

            data = ObjectDict(
                kind=1,  # // {0: success, 1: failure, 10: email}
                messages=messages,  # ['hello world', 'abjsldjf']
                button_text=msg.BACK_CN,
                button_link=self.make_url(path.PROFILE_VIEW,
                                          wechat_signature=self.get_argument('wechat_signature'),
                                          host=self.host),
                jump_link=None  # // 如果有会自动，没有就不自动跳转
            )

            self.render_page(template_name="system/user-info.html",
                             data=data)
            return


class ResumeImportHandler(BaseHandler):
    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):

        self.params.headimg = self.current_user.sysuser.headimg
        auth_api_url = "/{}/api/resume/import".format("m" if self.is_platform else "recruit")
        self.render(template_name='refer/neo_weixin/sysuser/importresume-auth.html', message='',
                    auth_api_url=auth_api_url)

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        """导入第三方简历（51job，智联招聘，猎聘，linkedin）
         异步导入简历专用类, 各种日志记录状态说明, 非负状态和爬虫状态保持一致
         0      正常
         1		用户名密码错误
         2		导入失败
         3		登陆失败
         4		登陆失败
        -1		请求异常，不支持该请求
        -2	    基础服务返回未识别状态
        -3		基础服务请求爬虫超时
        -4      导入超出限制
        -5      用户名密码错误,用户名, 密码没填写
        """

        username = self.params.get("_username", "")
        password = self.params.get("_password", "")
        captcha = self.params.get("linkedin_code", "")

        # 置空不必要参数，避免在 make_url 中被用到
        self.params.pop("recom_time", None)
        self.params.pop("ajax", None)
        self.params.pop("m", None)
        self.params.pop("abgroup", None)
        self.params.pop("tjtoken", None)
        self.params.pop("abapply", None)
        try:
            int(self.params.pid)
        except ValueError:
            self.params.pop('pid', None)

        if not username or not password:
            # 日志打点返回用户名和密码没有填写
            self.log_info = ObjectDict(
                status=-5,
                url=self.params.way
            )
            self.send_json_error(message=msg.RESUME_IMPORT_NAME_PASSWD_ERROR)
            return

        # 微信端用户只能导入一次简历，故不需要做导入频率限制，LinkedIn验证验证码使用该接口，如果做频率限制，LinkedIn验证需要单独接口
        if str(self.params.way) in const.RESUME_WAY_SPIDER:
            # 判断是否在微信端
            ua = 1 if self.in_wechat else 2
            is_ok, result = yield self.profile_ps.import_profile(
                const.RESUME_WAY_TO_INFRA.get(self.params.way, 0),
                username,
                password,
                self.current_user.sysuser.id,
                ua,
                self.current_user.wechat.company_id,
                captcha=captcha
            )
            if self.params.pid:
                next_url = self.make_url(path.PROFILE_PREVIEW, self.params)
            else:
                next_url = self.make_url(path.PROFILE_VIEW, self.params)

            if is_ok:
                self.log_info = ObjectDict(
                    status=0,
                    url=self.params.way
                )
                data = ObjectDict(url=next_url)
                self._log_customs.update(new_profile=const.YES)
                self.send_json_success(message=msg.RESUME_IMPORT_SUCCESS,
                                       data=data)

                return
            else:
                data = ObjectDict()
                if result.status == 32001:  # 埋点密码错误
                    status_log = 1
                elif result.status == 32002:  # 埋点导入失败
                    status_log = 2
                elif result.status == 32003:  # 埋点登陆失败
                    status_log = 3
                elif result.status == 32004:  # 埋点参数不正确
                    status_log = -5
                elif result.status == 32005:  # 埋点登陆失败
                    status_log = 4
                elif result.status == 32006:  # 埋点基础服务请求爬虫超时
                    status_log = -3
                elif result.status == 32007:  # 爬虫校验参数发现错误, 由于都是参数校验放一起
                    status_log = -5
                elif result.status == 32008:  # 简历导入次数超过每日次数限制
                    status_log = 5
                elif result.status == 32011:  # 需要输入LinkedIn验证码
                    status_log = 6
                    data.update(need_linkedin_verify=const.YES)
                    self.send_json_success(data=data)
                    self.log_info = ObjectDict(
                        status=status_log,
                        url=self.params.way,
                    )
                    return
                elif result.status == 32012:  # LinkedIn限制登录
                    status_log = 7
                    next_url = self.make_url(path.RESUME_IMPORT_FAIL, self.params)
                    data.update(url=next_url)
                elif result.status == 32013:  # 验证码失败
                    status_log = 8
                else:
                    # 埋点基础服务返回未识别异常
                    status_log = -2

                self.log_info = ObjectDict(
                    status=status_log,
                    url=self.params.way,
                )

                self.send_json_error(message=result.message if result.status != 32012 else "", data=data)

        else:
            self.log_info = ObjectDict(
                status=-1,
                url=self.params.way
            )

            self.send_json_error(message=msg.RESUME_IMPORT_FAILED)


class ResumeImportLimit(BaseHandler):
    """简历导入被限制"""

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        self.render(template_name='adjunct/lock-alert.html')


class LiepinImportCallBackHandler(MetaBaseHandler):
    @handle_response
    @gen.coroutine
    def get(self):
        """列聘授权回调接口"""
        self.logger.info('%s, request params: %s' % (self.__class__.__name__, self.params))

        user_id = match_session_id(
            to_str(self.get_secure_cookie(const.COOKIE_SESSIONID))
        )

        k = const.LIEPIN_SCENE_KEY_FMT.format(sysuser_id=user_id)
        scene_data = self.redis.get(k)

        if not scene_data:
            self.write_error(404)
            return

        scene_data = json.loads(scene_data)
        # 更新猎聘返回的openid,code
        scene_data.update(dict(
            openid=self.params.openid,
            code=self.params.code
        ))

        url = path.RESUME_LIEPIN.format(
            self.host,
            '?' + urllib.parse.urlencode(scene_data)
        )

        self.logger.info('%s, redirect url: %s' % (self.__class__.__name__, url))
        self.redirect(url)


class LiepinImportHandler(BaseHandler):
    """猎聘导入简历
    """

    @handle_response
    @gen.coroutine
    def get(self):
        self.logger.info('%s, request params:%s' % (self.__class__.__name__, self.params))

        openid = self.params.openid
        code = self.params.code
        if not openid and code:
            self.write_error(404)
            return

        user_id = match_session_id(
            to_str(self.get_secure_cookie(const.COOKIE_SESSIONID))
        )

        ua = 1 if self.in_wechat else 2

        # 通过基础服务　将 code openid appid　等参数发往 scraper项目去爬去简历
        is_ok, result = yield self.profile_ps.import_profile(
            const.FROM_LIEPIN,
            "",
            "",
            user_id,
            ua,
            token=code,
            unionid=openid,
            appid=self.settings.liepin_appid,
            version=1.0
        )
        if not is_ok:
            self.logger.info('%s, get resume failed. result: %s' %
                             (self.__class__.__name__, result))

            self.error_page(messages=result.message)

        else:
            # 获取简历成功后清楚缓存的场景数据
            self.redis.delete(const.LIEPIN_SCENE_KEY_FMT.format(sysuser_id=user_id))

            self.redirect(
                make_url(
                    path=path.PROFILE_PREVIEW if self.params.pid else path.PROFILE_VIEW,
                    params=self.params,
                    host=self.host
                )
            )

    def error_page(self, messages):
        data = ObjectDict(
            kind=1,  # // {0: success, 1: failure, 10: email}
            messages=messages,  # ['hello world', 'abjsldjf']
            button_text=msg.BACK_CN,
            button_link=self.make_url(
                path.PROFILE_VIEW,
                wechat_signature=self.get_argument('wechat_signature'),
                host=self.host
            ),
            jump_link=None  # // 如果有会自动，没有就不自动跳转
        )
        self.render_page(
            template_name="system/user-info.html",
            data=data
        )
