# coding=utf-8

from tornado import gen
from handler.base import BaseHandler

import conf.common as const
import conf.message as msg
from util.common.decorator import handle_response, verified_mobile_oneself, authenticated
from util.tool.str_tool import gen_salary, email_validate, is_alphabet, is_chinese, password_crypt
from util.tool.date_tool import jd_update_date, curr_now
from util.image.upload import QiniuUpload
from util.common import ObjectDict


class UsercenterHandler(BaseHandler):
    """个人中心首页, 单页应用。以 api 形式提供
    """

    @handle_response
    @gen.coroutine
    def put(self):

        try:
            # 重置 event，准确描述
            method = self.json_args.get("$key")
            self._event = self._event + method
            yield getattr(self, 'put_' + method)()
        except Exception as e:
            self.send_json_error()

    @handle_response
    @gen.coroutine
    def get(self):
        """
        个人中心首页
        :return:
        """
        # 手动指定 event
        self._event = self._event + "home"
        employee = yield self.user_ps.get_valid_employee_by_user_id(
            self.current_user.sysuser.id, self.current_user.company.id)
        # 查询该公司是否开启了员工认证
        employee_cert_conf = yield self.user_ps.get_employee_cert_conf(self.current_user.company.id)
        res = yield self.usercenter_ps.get_user(self.current_user.sysuser.id)

        self.send_json_success(data=ObjectDict(
            headimg=self.static_url(res.data.headimg or const.SYSUSER_HEADIMG),
            name=res.data.name or res.data.nickname,
            email=res.data.email,
            mobile=res.data.mobile,
            bind_disable=employee_cert_conf.disable == const.OLD_YES if employee_cert_conf else False,  # 该公司是否启用了认证
            bind_status=int(employee.activation) if employee else 1,
            has_password=True if res.data.password else False,
        ))

    @handle_response
    @authenticated
    @gen.coroutine
    def put_name(self):
        """配置-真实姓名"""

        try:
            self.guarantee('name')
        except:
            raise gen.Return()

        if is_chinese(self.params.name) or is_alphabet(self.params.name):
            res = yield self.usercenter_ps.update_user(self.current_user.sysuser.id, params={
                "name": self.params.name,
            })

            if res.status == const.API_SUCCESS:
                self.send_json_success()
                return
            else:
                self.send_json_error(message=msg.INPUT_DISORDER)
                return
        else:
            self.logger.debug(3)
            self.send_json_error(message=msg.OPERATE_FAILURE)

    @handle_response
    @verified_mobile_oneself
    @authenticated
    @gen.coroutine
    def put_email(self):
        """配置-Email"""

        try:
            self.guarantee('email')
        except:
            raise gen.Return()

        if email_validate(self.params.email):
            res = yield self.usercenter_ps.update_user(self.current_user.sysuser.id, params={
                "email": self.params.email,
            })
            if res.status == const.API_SUCCESS:
                self.send_json_success()
                return
        else:
            self.send_json_error(message=msg.OPERATE_FAILURE)

    @handle_response
    @verified_mobile_oneself
    @authenticated
    @gen.coroutine
    def put_password(self):
        """配置-修改密码"""

        try:
            self.guarantee('password')
        except:
            raise gen.Return()

        res = yield self.usercenter_ps.post_resetpassword(self.current_user.sysuser.username,
                                                          password_crypt(self.params.password))
        if res.status != const.API_SUCCESS:
            self.send_json_error(message=res.message)
            raise gen.Return()

        self.send_json_success()


class FavpositionHandler(BaseHandler):
    """个人中心-收藏职位"""

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """
        收藏记录
        :return:
        """

        res = yield self.usercenter_ps.get_fav_positions(self.current_user.sysuser.id)
        self.send_json_success(data=ObjectDict(records=res))


class ApplyrecordsHandler(BaseHandler):
    """个人中心-求职记录"""

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self, apply_id):
        """
        求职记录
        :return:
        """

        if apply_id:
            # 查看具体申请记录的进度
            res = yield self.usercenter_ps.get_applied_progress(apply_id, self.current_user.sysuser.id)
            self.logger.debug("get_applied_progress: %s" % res)
            self.send_json_success(data=res)

        else:
            # 查看申请记录列表
            res = yield self.usercenter_ps.get_applied_applications(self.current_user.sysuser.id)
            self.logger.debug("get_applied_applications: %s" % res)
            self.send_json_success(data=ObjectDict(
                records=res
            ))

class UploadHandler(BaseHandler):
    """图片上传
    """

    @handle_response
    @gen.coroutine
    def post(self, method):
        try:
            # 重置 event，准确描述
            self._event = self._event + method
            yield getattr(self, 'post_' + method)()
        except Exception as e:
            self.send_json_error()

    @handle_response
    @authenticated
    @gen.coroutine
    def post_avatar(self):
        """配置-设置头像"""

        res = yield self.usercenter_ps.get_user(self.current_user.sysuser.id)
        if res.data:
            vfile = self.request.files.get('vfile', None)
            if vfile is None:
                self.send_json_error()
                return

            body = vfile[0].get('body')
            upload_settings = dict()
            upload_settings['filename'] = vfile[0].get('filename')
            upload_settings[
                'filename_prefix'] = "upload/avatar/{}".format(self.current_user.sysuser.id)
            upload_settings['max_filesize'] = 1024 * 1024 * 2  # MB
            upload_settings['min_width'] = 30  # px
            upload_settings['before_upload'] = ['expand', 'crop']
            upload_settings['filter_expand'] = {
                "width": 300,
                "height": 300,
            }

            uploader = QiniuUpload(upload_settings)
            uploader.set_logger(self.logger)
            result = uploader.upload_bytes(body)

            if result.status != const.API_SUCCESS:
                self.send_json_error(message=result.message)
                return

            res = yield self.usercenter_ps.update_user(self.current_user.sysuser.id, params={
                "headimg": result.data,
            })

            if res.status == const.API_SUCCESS:
                self.send_json_success(data={
                    "url": self.static_url(result.data)
                })
            else:
                self.send_json_error()

        else:
            self.send_json_error()
