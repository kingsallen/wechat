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
    @authenticated
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
    @authenticated
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

        # res = yield self.usercenter_ps.get_fav_positions(self.current_user.sysuser.id)
        res = ObjectDict({
            "status": 0,
            "message": "SUCCESS",
            "data": [
                {
                    "id": 2,
                    "title": "职位名称1",
                    "department": "部门名称1",
                    "time": "2017-01-02 12:23:34", # 收藏的时间
                    "city": "上海，北京",
                    "salary_top": 34,
                    "salary_bottom": 10,
                    "update_time": curr_now(),  # 职位更新时间
                    "status": 0 # 职位状态
                },
                {
                    "id": 3,
                    "title": "职位名称2",
                    "department": "部门名称2",
                    "time": "2017-01-02 12:23:34",
                    "city": "上海，北京，南京",
                    "salary_top": 4,
                    "salary_bottom": 0,
                    "update_time": curr_now(),
                    "status": 2
                },
                {
                    "id": 4,
                    "title": "职位名称3",
                    "department": "部门名称3",
                    "time": "2017-01-02 12:23:34",
                    "city": "上海，北京，南京",
                    "salary_top": 0,
                    "salary_bottom": 0,
                    "update_time": curr_now(),
                    "status": 2
                },
            ]
        })
        if res.status == const.API_SUCCESS:
            for item in res.data:
                item['salary'] = gen_salary(item['salary_top'], item['salary_bottom'])
                item['update_time'] = jd_update_date(item['update_time'])
                item['states'] = "已过期" if item['status'] == 2 else ""

        self.send_json_success(data=ObjectDict(
            records=res.data
        ))


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
            # res = yield self.usercenter_ps.get_applied_progress(apply_id, self.current_user.sysuser.id)
            res = ObjectDict({
                "status": 0,
                "message": "SUCCESS",
                "data": {
                    "pid": 2,
                    "position_title": "职位名称",
                    "company_name": "职位所属公司",
                    "step": 2, # 1, 2, 3 分别对应 ["投递简历", "面试", "入职"],
                    "step_status": 2, #0, 1, 2, 如果是0，说明没开始，如果是1, 则是这个步骤通过了，2是这个步骤不通过
                    "status_timeline": [
                        {
                            "date": '2016-08-01 19:01:09',
                            "event": '简历提交成功',
                            "hide": 0, # 是否隐藏这个历史记录
                            "step_status": 0, # 0, 1, 2
                        },

                        {
                            "date": '2016-08-01 19:02:11',
                            "event": 'HR查看了您的简历',
                            "hide": 0,
                            "step_status": 2,  #0, 1, 2
                        }
                    ]
                }
            })
            self.send_json_success(data=res.data)

        else:
            # 查看申请记录列表
            # res = yield self.usercenter_ps.get_applied_applications(self.current_user.sysuser.id)
            res = ObjectDict({
                "status": 0,
                "message": "SUCCESS",
                "data": [
                    {
                        "id": 2, #app_id
                        "position_title": "职位名称1",
                        "company_name": "公司名称1",  # 公司名称
                        "time": "2017-01-08 12:23:34", # 申请时间
                        "status_name": "HR查看了你的简历"  # 申请进度状态
                    },
                    {
                        "id": 3,
                        "position_title": "职位名称2",
                        "company_name": "公司名称2",
                        "time": "2017-01-02 12:23:34",
                        "status_name": "面试成功"
                    },
                    {
                        "id": 4,
                        "position_title": "职位名称3",
                        "company_name": "公司名称3",
                        "time": "2017-01-02 12:23:34",
                        "status_name": "已入职"
                    },
                ]
            })
            self.send_json_success(data=ObjectDict(
                records=res.data
            ))

class UploadHandler(BaseHandler):
    """图片上传
    """

    @handle_response
    @authenticated
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
