# coding=utf-8

from tornado import gen
from handler.base import BaseHandler

import conf.common as const
import conf.path as path
import conf.message as msg
from util.common.decorator import handle_response, verified_mobile_oneself
from util.tool.str_tool import gen_salary, email_validate
from util.tool.date_tool import jd_update_date
from util.tool.url_tool import make_url
from util.image.upload import QiniuUpload

class HomeHandler(BaseHandler):
    """个人中心首页, 渲染个人中心页面
    """

    @handle_response
    @gen.coroutine
    def get(self):

        employee = yield self.user_ps.get_valid_employee_by_user_id(
            self.current_user.sysuser.id, self.current_user.company.id)
        self.params._binding_state = int(employee.activation) if employee else 1
        res = yield self.usercenter_ps.get_user(self.current_user.sysuser.id)
        res.data.headimg = self.static_url(res.data.headimg or const.SYSUSER_HEADIMG)
        self.params.user = res.data

        self.logger.debug("home: %s" % self.params)

        self.render(template_name="refer/weixin/neo_sysuser/personalcenter.html")

class AppRecordsHandler(BaseHandler):
    """求职记录
    """

    @handle_response
    @gen.coroutine
    def get(self):

        res = yield self.usercenter_ps.get_applied_applications(self.current_user.sysuser.id)
        self.params.application = res.data
        self.logger.debug("home: %s" % self.params)

        self.render(template_name="refer/weixin/sysuser/applicationrecord_new.html")

class FavPositionsHandler(BaseHandler):
    """感兴趣的职位
    """

    @handle_response
    @gen.coroutine
    def get(self):

        res = yield self.usercenter_ps.get_fav_positions(self.current_user.sysuser.id)
        if res.status == const.API_SUCCESS:
            for item in res.data:
                item['salary'] = gen_salary(item['salary_top'], item['salary_bottom'])
                item['update_time'] = jd_update_date(item['update_time'])
        self.params.position = res.data

        self.logger.debug("home: %s" % self.params)
        self.render(template_name="refer/weixin/sysuser/favoriteposition.html")

class UserSettingHandler(BaseHandler):
    """用户配置
    """

    @handle_response
    @gen.coroutine
    def get(self, method):

        self.logger.debug("method: %s" % method)
        self.logger.debug("re: %s" % self.request.arguments)


        try:
            yield getattr(self, 'get_' + method)()
        except Exception as e:
            self.write_error(404)

    @handle_response
    @gen.coroutine
    def get_home(self):
        """配置-首页"""

        res = yield self.usercenter_ps.get_user(self.current_user.sysuser.id)
        if res.data:
            self.params.user = res.data
            self.params._headimg = self.static_url(res.data.headimg or const.SYSUSER_HEADIMG)
            self.render(template_name="refer/neo_weixin/sysuser/accountconfig.html")
        else:
            self.write_error(404)

    @handle_response
    @gen.coroutine
    def get_name(self):
        """配置-真实姓名"""

        res = yield self.usercenter_ps.get_user(self.current_user.sysuser.id)
        if res.data:
            self.params._name = res.data.name or ''
            self.render(template_name="refer/weixin/sysuser/accountconfig-name.html")
        else:
            self.write_error(404)

    @handle_response
    @verified_mobile_oneself
    @gen.coroutine
    def get_email(self):
        """配置-Email"""

        res = yield self.usercenter_ps.get_user(self.current_user.sysuser.id)
        if res.data:
            self.params._email = res.data.email or ''
            self.render(template_name="refer/weixin/sysuser/accountconfig-email.html")
        else:
            self.write_error(404)

    @handle_response
    @verified_mobile_oneself
    @gen.coroutine
    def get_set_passwd(self):
        """配置-设置密码"""

        res = yield self.usercenter_ps.get_user(self.current_user.sysuser.id)
        if res.data.password is None:
            self.render(template_name="refer/weixin/sysuser/accountconfig-password.html")
        else:
            self.write_error(404)


    @handle_response
    @verified_mobile_oneself
    @gen.coroutine
    def get_change_passwd(self):
        """配置-修改密码"""

        res = yield self.usercenter_ps.get_user(self.current_user.sysuser.id)
        if res.data.password:
            self.params._mobile = res.data.mobile or ''
            self.render(template_name="refer/weixin/sysuser/accountconfig-password-mobilevalidate.html")
        else:
            self.write_error(404)

    @handle_response
    @gen.coroutine
    def post(self, method):
        try:
            yield getattr(self, 'post_' + method)()
        except Exception as e:
            self.send_json_error()

    @handle_response
    @gen.coroutine
    def post_name(self):
        # 配置-真实姓名
        try:
            self.guarantee('_name')
        except:
            return
        res = yield self.usercenter_ps.update_user(self.current_user.sysuser.id, params={
            "name": self.params._name,
        })
        if res.status == const.API_SUCCESS:
            self.redirect(make_url(path=path.USER_CENTER_SETTING))
        else:
            self.params.message = msg.OPERATE_FAILURE
            self.render(template_name="refer/weixin/sysuser/accountconfig-name.html")

    @handle_response
    @verified_mobile_oneself
    @gen.coroutine
    def post_email(self):
        # 配置-Email
        if email_validate(self.params._email):
            res = yield self.usercenter_ps.update_user(self.current_user.sysuser.id, params={
                "email": self.params._email,
            })
            if res.status == const.API_SUCCESS:
                self.redirect(make_url(path=path.USER_CENTER_SETTING))
        else:
            self.params.message = msg.OPERATE_FAILURE
            self.render(template_name="refer/weixin/sysuser/accountconfig-email.html")

    @handle_response
    @verified_mobile_oneself
    @gen.coroutine
    def post_change_passwd(self):
        # 配置-修改密码
        try:
            self.guarantee('_password')
        except:
            return

        res = yield self.usercenter_ps.update_user(self.current_user.sysuser.id, params={
            "password": self.params._password,
        })
        if res.status == const.API_SUCCESS:
            self.redirect(make_url(path=path.USER_CENTER_SETTING))
        else:
            self.params.message = msg.OPERATE_FAILURE
            self.render(template_name="refer/weixin/sysuser/accountconfig-password.html")

class UploadHandler(BaseHandler):
    """图片上传
    """

    @handle_response
    @gen.coroutine
    def post(self, method):
        try:
            yield getattr(self, 'post_' + method)()
        except Exception as e:
            self.send_json_error()

    @handle_response
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
            upload_settings['filename_prefix'] = "upload/avatar/{}".format(self.current_user.sysuser.id)
            upload_settings['max_filesize'] = 1024 * 1024 * 2  # MB
            upload_settings['min_width'] = 30  # px
            upload_settings['before_upload'] = ['expand', 'crop']
            upload_settings['filter_expand'] = {
                "width": 300,
                "height": 300,
            }

            # upload the avatar to qiniu
            uploader = QiniuUpload(upload_settings)
            uploader.set_logger(self.logger)
            result = uploader.upload_bytes(body)

            if result.status != const.API_SUCCESS:
                self.send_json_error()
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
