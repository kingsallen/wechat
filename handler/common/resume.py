# coding=utf-8

import json
from tornado import gen

import conf.path as path
import conf.message as msg
import conf.common as const
from handler.base import BaseHandler
from handler.metabase import MetaBaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated
from util.tool.str_tool import to_str, match_session_id


class LinkedinImportHandler(MetaBaseHandler):
    """
    linkedin 导入，由于 linkedin 为 oauth2.0导入，
    与微信 oauth2.0授权冲突（code问题），
    故直接继承 MetaBaseHandler"""

    @handle_response
    @gen.coroutine
    def get(self):

        code = self.params.code
        if not code:
            self.write_error(404)
            return

        user_id = match_session_id(to_str(self.get_secure_cookie(const.COOKIE_SESSIONID)))

        redirect_url = self.make_url(path.RESUME_LINKEDIN,
                                recom=self.params.recom,
                                pid=self.params.pid,
                                wechat_signature=self.params.wechat_signature)

        response = yield self.profile_ps.get_linkedin_token(code=code, redirect_url=redirect_url)
        response = json.loads(to_str(response))
        access_token = response.get("access_token")
        # 判断是否在微信端
        ua = 1 if self.in_wechat else 2
        is_ok, result = yield self.profile_ps.import_profile(4, "", "", user_id, ua, access_token)
        self.logger.debug("is_ok:{} result:{}".format(is_ok, result))
        if is_ok:
            if self.params.pid:
                next_url = self.make_url(path.PROFILE_VIEW, params=self.params, apply='1')
            else:
                next_url = self.make_url(path.PROFILE_VIEW, params=self.params)

            self.redirect(next_url)
            return
        else:
            self.write_error(500)


class ResumeImportHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):

        self.params.headimg = self.current_user.sysuser.headimg
        auth_api_url = "/{}/api/resume/import".format("m" if self.is_platform else "recruit")
        self.render(template_name='refer/neo_weixin/sysuser/importresume-auth.html', message='', auth_api_url=auth_api_url)

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

        # 微信端用户只能导入一次简历，故不需要做导入频率限制
        if self.params.way in const.RESUME_WAY_SPIDER.keys():
            # 判断是否在微信端
            ua = 1 if self.in_wechat else 2
            is_ok, result = yield self.profile_ps.import_profile(
                const.RESUME_WAY_TO_INFRA.get(self.params.way, 0),
                username,
                password,
                self.current_user.sysuser.id,
                ua
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
                self.send_json_success(message=msg.RESUME_IMPORT_SUCCESS,
                                       data={ "url": next_url })
                return
            else:
                if result.status == 32001:
                    # 埋点密码错误
                    status_log = 1
                elif result.status == 32002:
                    # 埋点导入失败
                    status_log = 2
                elif result.status == 32003:
                    # 埋点登陆失败
                    status_log = 3
                elif result.status == 32004:
                    # 埋点参数不正确
                    status_log = -5
                elif result.status == 32005:
                    # 埋点登陆失败
                    status_log = 4
                elif result.status == 32006:
                    # 埋点基础服务请求爬虫超时
                    status_log = -3
                elif result.status == 32007:
                    # 爬虫校验参数发现错误, 由于都是参数校验放一起
                    status_log = -5
                else:
                    # 埋点基础服务返回未识别异常
                    status_log = -2

                self.log_info = ObjectDict(
                    status=status_log,
                    url=self.params.way,
                )

                self.send_json_error(message=result.message)

        else:
            self.log_info = ObjectDict(
                status=-1,
                url=self.params.way
            )

            self.send_json_error(message=msg.RESUME_IMPORT_FAILED)
