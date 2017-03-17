# coding=utf-8

from tornado import gen

import conf.path as path
import conf.message as msg
import conf.common as const
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated
from util.tool.url_tool import make_url


class ResumeImportHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):

        self.params.headimg = self.current_user.sysuser.headimg
        self.render(template_name='neo_weixin/sysuser/importresume-auth.html', message='')


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

        username = self.json_args.get("_username", "")
        password = self.json_args.get("_password", "")

        if not username or not password:
            # 日志打点返回用户名和密码没有填写
            self.log_info = ObjectDict(
                status = -5,
                url = self.params.way
            )
            self.send_json_error(message=msg.RESUME_IMPORT_NAME_PASSWD_ERROR)
            return

        # 微信端用户只能导入一次简历，故不需要做导入频率限制
        if self.params.way in const.RESUME_WAY_SPIDER.keys():
            is_ok, result = yield self.profile_ps.import_profile(
                const.RESUME_WAY_TO_INFRA.get(self.params.way, 0),
                username,
                password,
                self.current_user.sysuser.id)

            if self.params.pid:
                next_url = make_url(path.APPLICATION+"/app", self.params)
            else:
                # TODO profile 预览页面
                next_url = make_url(path.APPLICATION + "/app", self.params)

            if is_ok:
                self.log_info = ObjectDict(
                    status = 0,
                    url = self.params.way
                )
                self.send_json_success(message=msg.RESUME_IMPORT_SUCCESS, data={
                    "url": next_url
                })
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
                    status = status_log,
                    url = self.params.way,
                )

                self.send_json_error(message=msg.RESUME_IMPORT_FAILED)

        else:
            self.log_info = ObjectDict(
                status = -1,
                url = self.params.way,
            )

            self.send_json_error(message=msg.RESUME_IMPORT_FAILED)
