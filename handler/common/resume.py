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
                                          self.params,
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
                                          self.params,
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
                #added by iris
                position = yield self.position_ps.get_position(self.params.pid, display_locale=self.get_current_locale())
                if position.app_cv_config_id:
                    next_url = self.make_url(path.PROFILE_CUSTOM_CV, self.params)
                else:
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
                    data.update(need_verify=const.YES)
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

        # 更新猎聘返回的openid,code
        scene_data.update(dict(
            open_id=self.params.open_id,
            liepin_code=self.params.code
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
        code = self.params.liepin_code
        if not code:
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
                self.params,
                host=self.host
            ),
            jump_link=None  # // 如果有会自动，没有就不自动跳转
        )
        self.render_page(
            template_name="system/user-info.html",
            data=data
        )


class ResumeUploadHandler(BaseHandler):
    """
    上传简历页面
    """

    @handle_response
    @gen.coroutine
    def get(self):
        self.render_page(template_name="profile/mobile-upload-resume-self.html",
                         data=ObjectDict())


class ChatbotResumeUploadHandler(BaseHandler):
    """
    Chatbot专用上传简历页面
    """

    @handle_response
    @gen.coroutine
    def get(self):
        data = {'for_sharing': False}
        relationship = yield self.dictionary_ps.get_referral_relationship(self.locale)
        data.update(consts=dict(relation=relationship))
        if self.params.get('for_sharing') == '1':
            api_data = (yield self.profile_ps.get_uploaded_profile(self.current_user.employee.id))['data']
            position_data = json.loads(self.params.get('data'))
            rids = [i['recommendation_id'] for i in position_data]
            pids = [i['id'] for i in position_data]
            name = api_data.pop('name')
            censored_name = name[0] + '*' * (len(name) - 1)
            data = {
                'for_sharing': True,
                'name': censored_name,
                'consts': dict(relation=relationship),
                **api_data,
            }
            self.logger.debug('data for rendering is %s' % data)
            self.params.share = yield self._make_share(
                dict(rkey=','.join(str(i) for i in rids),
                     pid=','.join(str(i) for i in pids),
                     wechat_signature=self.current_user.wechat.signature))
        self.render_page(template_name="chat/mobot-upload-resume.html", data=data)

    @gen.coroutine
    def _make_share(self, params):
        link = self.make_url(
            path.REFERRAL_CONFIRM,
            params,
            recom=self.position_ps._make_recom(self.current_user.sysuser.id))

        company_info = yield self.company_ps.get_company(
            conds={"id": self.current_user.company.id}, need_conf=True)

        cover = self.share_url(company_info.logo)

        share_info = ObjectDict({
            "cover": cover,
            "title": "【#name#】恭喜您已被内部员工推荐",
            "description": "点击查看详情~",
            "link": link
        })
        return share_info


class ChatbotResumeSubmitHandler(BaseHandler):
    @handle_response
    @gen.coroutine
    def post(self):
        args = self.json_args
        result = yield self.profile_ps.submit_upload_profile_from_chatbot(
            name=args.name,
            mobile=args.mobile,
            employee_id=self.current_user.employee.id,
            referral_reasons=args.referral_reasons,
            file_name=args.file_name,
            relationship=args.relation,
            recom_reason_text=args.comment
        )
        success = result.status == 0
        data = {'name': args.name, 'success': success}
        if success:
            data['referral_id'] = result.data
        url = '/m/mobot?hr_id={}&wechat_signature={}&flag=4&data={}&room_type={}'.format(
            self.json_args.hr_id,
            self.current_user.wechat.signature,
            urllib.parse.quote(json.dumps(data)),
            self.json_args.room_type or 1
        )
        self.send_json_success({'next_url': url})


class APIResumeUploadHandler(BaseHandler):
    """
    手机上传简历
    """

    @handle_response
    @gen.coroutine
    def post(self):
        if len(self.request.files) == 0:
            file_data = self.request.body
            file_name = self.get_argument("vfile")
        else:
            image = self.request.files["vfile"][0]
            file_data = image["body"]
            file_name = image["filename"]
        user_id = self.current_user.sysuser.id
        if len(file_data) > 2 * 1024 * 1024:
            self.send_json_error(message="请上传2M以下的文件")
            return

        ret = yield self.profile_ps.resume_upload(file_name, file_data, user_id)
        if ret.status != const.API_SUCCESS:
            self.send_json_error(message=ret.message)
            return
        else:
            self.send_json_success(data=ret.data)
            return


class ResumeSubmitHandler(BaseHandler):
    """
    简历上传成功
    """

    @handle_response
    @gen.coroutine
    def post(self):
        name = self.json_args.name
        mobile = self.json_args.mobile
        pid = self.json_args.pid
        result = yield self.profile_ps.submit_upload_profile(name, mobile, self.current_user.sysuser.id)
        if result.status != const.API_SUCCESS:
            self.send_json_error(message=result.message)
            return
        else:
            if pid:
                next_url = self.make_url(path.PROFILE_PREVIEW, self.params, pid=pid)
            else:
                next_url = self.make_url(path.PROFILE_VIEW, self.params, pid=pid)

            self.send_json_success(data={"next_url": next_url})
            return


class ResumeUploadResultHandler(BaseHandler):
    """
    在微信端页面扫码进入小程序上传完文件后，小程序退出返回到微信端页面，微信端页面需要知道上传结果。
    微信端页面拿到上传结果后，或者确认上传成功后，需要跳转到某个页面A，在页面A对该结果做处理。
    """

    @handle_response
    @gen.coroutine
    def get(self):
        sync_id = self.params.syncId
        employee_id = self.current_user.employee.id if self.current_user.employee else 0
        result = yield self.profile_ps.is_resume_upload_complete(self.current_user.sysuser.id, sync_id, employee_id)
        if result.status == const.API_SUCCESS:
            self.send_json_success({"finished": result.data})
        else:
            self.send_json_error(message=result.message)


class MiniappResumeUploadInfoHandler(BaseHandler):
    """
    通过上传助手小程序上传后的简历信息
    """

    @handle_response
    @gen.coroutine
    def get(self):
        sync_id = self.params.syncId
        employee_id = self.current_user.employee.id if self.current_user.employee else 0
        result = yield self.profile_ps.referral_upload_resume_info(self.current_user.sysuser.id, sync_id, employee_id)
        if result.status == const.API_SUCCESS:
            self.send_json_success(result.data)
        else:
            self.send_json_error(message=result.message)










