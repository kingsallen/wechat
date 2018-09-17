# coding=utf-8

from tornado import gen
from handler.base import BaseHandler

import conf.common as const
import conf.message as msg
from thrift_gen.gen.employee.struct.ttypes import BindStatus
from util.common.decorator import handle_response, verified_mobile_oneself, authenticated, check_employee_common
from util.tool.str_tool import email_validate, is_alphabet, is_chinese, password_crypt, password_validate
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
            yield getattr(self, "put_" + method)()
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

        # 查询该公司是否开启了员工认证
        employee_cert_conf = yield self.user_ps.get_employee_cert_conf(
            self.current_user.company.id)
        if not self.current_user.sysuser.id:
            res = ObjectDict(data=ObjectDict)
        else:
            res = yield self.usercenter_ps.get_user(self.current_user.sysuser.id)

        # 检查员工绑定状态
        bind_status = yield self.employee_ps.get_employee_bind_status(
            self.current_user.sysuser.id,
            self.current_user.company.id
        )
        fe_bind_status = self.employee_ps.convert_bind_status_from_thrift_to_fe(
            bind_status)
        if fe_bind_status == 0:
            unread_praise = yield self.employee_ps.get_unread_praise(self.current_user.employee.id)
        else:
            unread_praise = 0
        self.send_json_success(data=ObjectDict(
            headimg=self.static_url(res.data.headimg or const.SYSUSER_HEADIMG),
            name=res.data.name or res.data.nickname,
            email=res.data.email,
            mobile_display=self.current_user.sysuser.mobile_display,  # do not pass '0' to FE
            # 该公司是否启用了认证
            bind_disable=employee_cert_conf.disable == const.OLD_NO,
            bind_status=fe_bind_status,
            has_password=bool(res.data.password),
            unread_praise=unread_praise
        ))

    @handle_response
    @authenticated
    @gen.coroutine
    def put_name(self):
        """配置-真实姓名"""

        try:
            self.guarantee("name")
        except:
            return

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
            self.guarantee("email")
        except:
            return

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
            self.guarantee("password")
        except:
            return

        if not password_validate(self.params.password):
            self.send_json_error(message=msg.CELLPHONE_PASSWORD_ERROR)
            raise gen.Return()

        res = yield self.usercenter_ps.post_resetpassword(self.current_user.sysuser.country_code,
                                                          self.current_user.sysuser.username,
                                                          self.params.password)
        if res.status != const.API_SUCCESS:
            self.send_json_error(message=res.message)
            raise gen.Return()

        self.send_json_success()


class UsercenterMineHandler(BaseHandler):
    """认证员工个人中心-我的"""

    @handle_response
    @check_employee_common
    @gen.coroutine
    def get(self):
        data = ObjectDict({
            "referral_me": self.locale.translate("referral_me")
        })
        self.render_page(template_name="employee/me.html", data=data)


class UsercenterMyInfoHandler(BaseHandler):
    """认证员工个人中心-我的信息"""

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):

        if not self.current_user.sysuser.id:
            res = ObjectDict(data=ObjectDict)
        else:
            res = yield self.usercenter_ps.get_my_info(self.current_user.sysuser.id, self.current_user.company.id)

        # 检查员工绑定状态
        bind_status = yield self.employee_ps.get_employee_bind_status(
            self.current_user.sysuser.id,
            self.current_user.company.id
        )
        fe_bind_status = self.employee_ps.convert_bind_status_from_thrift_to_fe(
            bind_status)
        if fe_bind_status == 0:
            unread_praise = yield self.employee_ps.get_unread_praise(self.current_user.employee.id)
        else:
            unread_praise = 0
        self.send_json_success(data=ObjectDict(
            headimg=self.static_url(res.data.headimg or const.SYSUSER_HEADIMG),
            name=res.data.name,
            bind_status=fe_bind_status,
            unread_praise=unread_praise
        ))


class FavPositionHandler(BaseHandler):
    """个人中心-收藏职位"""

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """
        收藏记录
        :return:
        """

        res = yield self.usercenter_ps.get_collect_positions(self.current_user.sysuser.id)
        self.send_json_success(data=ObjectDict(records=res))


class ApplyRecordsHandler(BaseHandler):
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
            try:
                res = yield self.usercenter_ps.get_applied_progress(self.current_user.sysuser.id, apply_id)
                self.send_json_success(data=res)
            except Exception as e:
                self.send_json_error()
                self.logger.error('get apply record in detail failed. error_msg{}'.format(e))

        else:
            # 查看申请记录列表
            res = yield self.usercenter_ps.get_applied_applications(self.current_user.sysuser.id, self.current_user.company.id)
            self.send_json_success(data=ObjectDict(
                records=res
            ))


class UserMobileBindedHandler(BaseHandler):
    """是否绑定了手机号"""

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):

        if self.current_user.sysuser.mobileverified:
            self.send_json_success(data=const.YES)
        else:
            self.send_json_success(data=const.NO)


class UploadHandler(BaseHandler):
    """图片上传
    """

    @handle_response
    @gen.coroutine
    def post(self, method):
        try:
            # 重置 event，准确描述
            self._event = self._event + method
            yield getattr(self, "post_" + method)()
        except Exception as e:
            self.send_json_error()

    @handle_response
    @authenticated
    @gen.coroutine
    def post_avatar(self):
        """配置-设置头像"""

        res = yield self.usercenter_ps.get_user(self.current_user.sysuser.id)
        if res.data:
            upload_settings = ObjectDict()
            upload_settings[
                "filename_prefix"] = "upload/avatar/{}".format(self.current_user.sysuser.id)
            upload_settings["before_upload"] = ["expand", "crop"]
            upload_settings["filter_expand"] = {
                "width": 300,
                "height": 300,
            }

            result = self._upload(upload_settings)
            if result is None:
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

    @handle_response
    @authenticated
    @gen.coroutine
    def post_school_logo(self):
        """proifle，上传学校 logo"""

        upload_settings = ObjectDict()
        upload_settings["filename_prefix"] = "upload/college_logo"
        upload_settings["before_upload"] = ["crop", "resize"]
        upload_settings["filter_resize"] = {
            "width": 300,
            "height": 300,
        }

        result = self._upload(upload_settings)
        if result is None:
            return

        self.send_json_success(data={
            "url": result.data
        })

    @handle_response
    @authenticated
    @gen.coroutine
    def post_company_logo(self):
        """proifle，上传公司 logo"""

        upload_settings = ObjectDict()
        upload_settings["filename_prefix"] = "upload/company_logo"
        upload_settings["before_upload"] = ["crop", "resize"]
        upload_settings["filter_resize"] = {
            "width": 300,
            "height": 300,
        }

        result = self._upload(upload_settings)
        if result is None:
            return
        self.send_json_success(data={
            "url": result.data
        })

    @handle_response
    @authenticated
    @gen.coroutine
    def post_link_banner(self):
        """proifle，上传链接图片"""

        upload_settings = ObjectDict()
        upload_settings[
            "filename_prefix"] = "upload/profile_link_banner/{}".format(self.current_user.sysuser.id)
        upload_settings["before_upload"] = ["expand", "crop"]
        # will resize image to 460x287
        upload_settings["filter_expand"] = {
            "width": 460,
            "height": 287,
        }
        upload_settings["filter_crop"] = {
            "width": 460,
            "height": 287
        }

        result = self._upload(upload_settings)
        if result is None:
            return
        self.send_json_success(data={
            "url": result.data
        })

    @handle_response
    @authenticated
    @gen.coroutine
    def post_profile_portrait(self):
        """prifle，上传证件照"""

        upload_settings = ObjectDict()
        upload_settings[
            "filename_prefix"] = "upload/profile_portrait/{}".format(self.current_user.sysuser.id)
        upload_settings["before_upload"] = ["expand", "crop"]
        # will resize image to 300x300
        upload_settings["filter_expand"] = {
            "width": 300,
            "height": 300,
        }

        result = self._upload(upload_settings)
        if result is None:
            return
        self.send_json_success(data={
            "url": result.data
        })

    def _upload(self, upload_settings):

        vfile = self.request.files.get("vfile", None)

        if vfile is None:
            self.send_json_error(message="上传参数错误")
            return None

        upload_settings.update({
            "filename": vfile[0].get("filename"),
            "max_filesize": 1024 * 1024 * 2,  # MB
            "min_width": 30,  # px
        })

        uploader = QiniuUpload(upload_settings)
        uploader.set_logger(self.logger)
        body = vfile[0].get("body")
        result = uploader.upload_bytes(body)

        self.logger.debug("[_upload]reusult:{}".format(result))

        if result.status != const.API_SUCCESS:
            self.send_json_error(message=result.message)
            return

        return result
