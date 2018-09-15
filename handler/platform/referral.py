# coding=utf-8

from tornado import gen

import conf.common as const
import conf.path as path
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated, check_employee_common
import conf.message as msg


class ReferralProfileHandler(BaseHandler):
    """微信端推荐人才简历"""

    @handle_response
    @authenticated
    @check_employee_common
    @gen.coroutine
    def get(self):
        pid = self.params.pid
        reward = yield self.employee_ps.get_bind_reward(self.current_user.company.id, const.REWARD_UPLOAD_PROFILE)
        position_info = yield self.position_ps.get_position(pid)

        self.params.share = yield self._make_share()
        self.render_page(template_name="employee/mobile-upload-resume.html",
                         data=ObjectDict({
                             "points": reward,
                             "job_title": position_info.title,
                             "upload_resume": self.locale.translate("referral_upload")}
                         ))

    @gen.coroutine
    def _make_share(self):
        link = self.make_url(
            path.REFERRAL_CONFIRM,
            self.params,
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


class ReferralProfileAPIHandler(BaseHandler):
    """微信端推荐人才简历api"""

    @handle_response
    @gen.coroutine
    def post(self):
        yield self._post(type=1)

    @handle_response
    @gen.coroutine
    def _post(self, type=1,):
        name = self.json_args.name
        mobile = self.json_args.mobile
        recom_reason = self.json_args.recom_reason
        pid = self.json_args.pid
        user_info = yield self.employee_ps.get_employee_info_by_user_id(self.current_user.sysuser.id)
        employee_id = self.current_user.employee.id if not user_info.employee_id else user_info.employee_id
        res = yield self.employee_ps.update_recommend(employee_id, name, mobile, recom_reason, pid,
                                                      type)
        if res.status == const.API_SUCCESS:
            if type == 1:
                self.send_json_success(data=ObjectDict({
                    "rkey": res.data
                }))
            elif type == 2:
                url = self.make_url(path.REFERRAL_SCAN, float=1, wechat_signature=user_info.wechat_signature, pid=pid, rkey=res.data)
                logo = self.current_user.company.logo
                qrcode = yield self.employee_ps.get_referral_qrcode(url, logo)
                self.send_json_success(data=ObjectDict({
                    "wechat": {"qrcode": qrcode.data}
                }))
        else:
            self.send_json_error()


class EmployeeRecomProfileHandler(BaseHandler):
    """上传简历"""

    @handle_response
    @gen.coroutine
    def post(self):
        yield self._post()

    @handle_response
    @gen.coroutine
    def _post(self, employee_id=None):
        if len(self.request.files) == 0:
            file_data = self.request.body
            file_name = self.get_argument("vfile")
        else:
            image = self.request.files["vfile"][0]
            file_data = image["body"]
            file_name = image["filename"]

        if len(file_data) > 2 * 1024 * 1024:
            self.send_json_error(message="请上传2M以下的文件")
            return
        if not employee_id:
            employee_id = self.current_user.employee.id
        ret = yield self.employee_ps.upload_recom_profile(file_name, file_data, employee_id)
        if ret.status != const.API_SUCCESS:
            self.send_json_error(message=ret.message)
            return
        else:
            self.send_json_success(data=ret.data)
            return


class ReferralConfirmHandler(BaseHandler):
    """推荐成功"""

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        if not self.current_user.sysuser.username.isdigit():
            type = 1
        else:
            if self.current_user.wxuser.is_subscribe or self.current_user.wechat.type == 0:
                type = 2
            else:
                type = 3
        wechat = yield self.wechat_ps.get_wechat_info(self.current_user,
                                                      pattern_id=const.QRCODE_REFERRAL_CONFIRM if type == 1 else const.QRCODE_OTHER,
                                                      in_wechat=self.in_wechat)
        rid = self.params.rkey
        ret = yield self.employee_ps.get_referral_info(rid)
        key = const.CONFIRM_REFERRAL_MOBILE.format(rid, self.current_user.sysuser.id)
        self.redis.set(key, ObjectDict(mobile=ret.data.mobile), ttl=60 * 60 * 24)
        body = ret.data
        if ret.status != const.API_SUCCESS or body.get("claim") is not False:
            type = 4
            body = ObjectDict()
        data = ObjectDict({
            "type": type,
            "successful_recommendation": self.locale.translate("referral_success"),
            "variants": {
                "presentee_first_name": body.employee_name,
                "recom_name": body.user_name[0:1] + "**",
                "company_name": body.company_abbreviation,
                "position_title": body.position,
                "new_user": body.user_name[0:1] + "**",
                "apply_id": body.apply_id,
                "mobile": body.mobile[0:3] + "****" + body.mobile[-4:],
                "wechat": wechat}
        })
        self.render_page(template_name="employee/recom-presentee-confirm.html", data=data)


class ReferralConfirmApiHandler(BaseHandler):
    """推荐成功api"""

    @handle_response
    @gen.coroutine
    def post(self):
        if self.current_user.sysuser.username.isdigit():
            try:
                self.guarantee("name", "rkey")
            except AttributeError:
                raise gen.Return()
            data = ObjectDict({
                "name": self.params.name,
                "referral_record_id": self.params.rkey,
                "user": self.current_user.sysuser.id
            })
            ret = yield self.employee_ps.confirm_referral_info(data)
        else:
            try:
                self.guarantee("name", "vcode", "rkey")
            except AttributeError:
                raise gen.Return()
            mobile = self.json_args.mobile
            if not mobile:
                mobile = self.redis.get(
                    const.CONFIRM_REFERRAL_MOBILE.format(self.params.rkey, self.current_user.sysuser.id)).get('mobile')
            data = ObjectDict({
                "name": self.params.name,
                "mobile": mobile,
                "vcode": self.params.vcode,
                "referral_record_id": self.params.rkey,
                "user": self.current_user.sysuser.id
            })
            ret = yield self.employee_ps.confirm_referral_info(data)
        if ret.status != const.API_SUCCESS:
            self.send_json_error(message=ret.message)
            return
        else:
            self.send_json_success(data=ret.data)
            return


class ReferralProfilePcHandler(BaseHandler):
    """手机扫码pc上传简历"""

    @handle_response
    @authenticated
    @check_employee_common
    @gen.coroutine
    def get(self):
        pid = self.params.pid
        float = self.params.float
        rkey = self.params.rkey
        key = const.UPLOAD_RECOM_PROFILE.format(self.current_user.sysuser.id)
        self.redis.set(key, ObjectDict(pid=pid), ttl=60 * 60 * 24)
        reward = yield self.employee_ps.get_bind_reward(self.current_user.company.id, const.REWARD_UPLOAD_PROFILE)
        yield self.employee_ps.update_referral_position(self.current_user.employee.id, pid)
        data = ObjectDict({
            "points": reward
        })
        if float:
            ret = yield self.employee_ps.get_referral_info(rkey)
            data.update(float=1,
                        username=ret.data.user_name,
                        job_title=ret.data.position,
                        rkey=rkey)
        self.render_page(template_name="employee/recom-scan-qrcode.html", data=data)


class ReferralCrucialInfoHandler(BaseHandler):
    """关键信息推荐"""

    @handle_response
    @authenticated
    @check_employee_common
    @gen.coroutine
    def get(self):
        pid = self.params.pid
        position_info = yield self.position_ps.get_position(pid)
        reward = yield self.employee_ps.get_bind_reward(self.current_user.company.id, const.REWARD_UPLOAD_PROFILE)
        title = position_info.title
        self.params.share = yield self._make_share()
        self.render_page(template_name="employee/recom-candidate-info.html", data=ObjectDict({
            "job_title": title,
            "points": reward
        }))

    @gen.coroutine
    def _make_share(self):
        link = self.make_url(
            path.REFERRAL_CONFIRM,
            self.params,
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


class ReferralCrucialInfoApiHandler(BaseHandler):
    """提交关键信息"""

    @handle_response
    @gen.coroutine
    def post(self):
        ret = yield self.employee_ps.update_referral_crucial_info(self.current_user.employee.id, self.json_args)
        if ret.status != const.API_SUCCESS:
            self.send_json_error(message=ret.message)
            return
        else:
            self.send_json_success(data=ObjectDict({
                "rkey": ret.data
            }))
            return
