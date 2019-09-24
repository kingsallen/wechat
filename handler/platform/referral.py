# coding=utf-8

from tornado import gen

import conf.common as const
import conf.message as msg
import conf.path as path
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated, check_employee_common
from util.tool.str_tool import json_underline2hump, json_hump2underline
from util.common.exception import InfraOperationError


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
        data = yield self.company_ps.get_only_referral_reward(self.current_user.company.id)
        reward = reward if not data.flag or (data.flag and position_info.is_referral) else 0

        position_template = yield self.position_ps.get_position_template_by_pids(pid=pid)
        if position_template.code != const.NEWINFRA_API_SUCCESS:
            raise InfraOperationError(position_template.message)
        fields = {}
        for field in position_template.data.fields:
            if field.get("field_name") == "fullnamepinyin":
                fields["pinyin_name"] = {"required": not int(field.get("required")), "validate_re": field.get("validate_re")}
            if field.get("field_name") == "familynamepinyin":
                fields["pinyin_surname"] = {"required": not int(field.get("required")), "validate_re": field.get("validate_re")}
            if field.get("field_name") == "email":
                fields["email"] = {"required": not int(field.get("required")), "validate_re": field.get("validate_re")}

        self.params.share = yield self._make_share()
        relationship = yield self.dictionary_ps.get_referral_relationship(self.locale)
        self.render_page(template_name="employee/mobile-upload-resume.html",
                         data=ObjectDict({
                             "points": reward,
                             "job_title": position_info.title,
                             "fields": fields,
                             "upload_resume": self.locale.translate("referral_upload"),
                             "consts": dict(
                                 relation=relationship
                             )
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


class ReferralProfileAPIHandler(BaseHandler):
    """微信端推荐人才简历api"""

    @handle_response
    @gen.coroutine
    def post(self):
        yield self._post(type=1)

    @handle_response
    @gen.coroutine
    def _post(self, type=1):
        name = self.json_args.name
        mobile = self.json_args.mobile
        recom_reason = self.json_args.recom_reason
        relationship = self.json_args.relation
        recom_reason_text = self.json_args.comment
        pid = self.json_args.pid
        upload_from = self.json_args.upload_from or 0
        email = self.json_args.email
        family_name_pinyin = self.json_args.pinyin_surname
        full_name_pinyin = self.json_args.pinyin_name

        user_info = yield self.employee_ps.get_employee_info_by_user_id(self.current_user.sysuser.id)
        employee_id = self.current_user.employee.id if not user_info.employee_id else user_info.employee_id
        # 神策埋点
        self._add_sensor_track(type, upload_from)

        res = yield self.employee_ps.update_recommend(employee_id, name, mobile, recom_reason, pid,
                                                      type, relationship, recom_reason_text, email, family_name_pinyin, full_name_pinyin)
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
            self.send_json_error(message=res.message)

    def _add_sensor_track(self, type, upload_from):
        if type == 1:
            if int(upload_from) == 2:
                self.track("directReferral", properties={"apply_origin": const.SA_DIRECT_REFERRAL_ORIGIN_WECHAT_UPLOAD})
            else:
                self.track("directReferral", properties={"apply_origin": const.SA_DIRECT_REFERRAL_ORIGIN_PHONE_UPLOAD})
        else:
            self.track("directReferral", properties={"apply_origin": const.SA_DIRECT_REFERRAL_ORIGIN_PC_UPLOAD})


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
        if ret.code != const.NEWINFRA_API_SUCCESS:
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
        rkey = self.params.rkey
        rids = rkey.split(',')
        recommendations = [ObjectDict({**data, 'rid': rid}) for data, rid in
                           zip((yield [self.employee_ps.get_referral_info(rid) for rid in rids]), rids)]
        failed_recommendations = [r for r in recommendations if r.status != const.API_SUCCESS]
        claimed_recommendations = [r for r in recommendations if
                                   r.status == const.API_SUCCESS and r['data']['claim']]
        unclaimed_recommendations = [r for r in recommendations if
                                     r.status == const.API_SUCCESS and not r['data']['claim']]
        if not claimed_recommendations and not unclaimed_recommendations:
            data = ObjectDict(
                kind=1,  # // {0: success, 1: failure, 10: email}
                messages=[recommendations[0].message],  # ['hello world', 'abjsldjf']
                button_text=msg.BACK_CN,
                button_link=self.make_url(path.POSITION_LIST,
                                          self.params,
                                          host=self.host),
                jump_link=None  # // 如果有会自动，没有就不自动跳转
            )

            return self.render_page(template_name="system/user-info.html",
                                    data=data)

        if not self.current_user.sysuser.username.isdigit():
            type = 1
        elif claimed_recommendations and not unclaimed_recommendations:
            type = 4
        elif self.current_user.wxuser.is_subscribe or self.current_user.wechat.type == 0:
            type = 2
        else:
            type = 3

        pattern_id = const.QRCODE_REFERRAL_CONFIRM if type == 1 else const.QRCODE_OTHER
        scene_id = int('11110000000000000000000000000000', base=2) + pattern_id
        wechat = yield self.wechat_ps.get_wechat_info(
            self.current_user,
            scene_id=scene_id,
            in_wechat=self.in_wechat)

        data_sample = recommendations[0].data

        valid_rkeys = [r.rid for r in unclaimed_recommendations]
        if data_sample.mobile:
            self.redis.set(const.CONFIRM_REFERRAL_MOBILE.format(','.join(valid_rkeys), self.current_user.sysuser.id),
                           ObjectDict(mobile=data_sample.mobile), ttl=60 * 60 * 24)
        if self.current_user.employee and self.current_user.employee.id == data_sample.employee_id:
            in_person = True
        else:
            in_person = False

        # 对姓名做隐藏处理
        if len(data_sample.user_name.split()) == 1:
            presentee_first_name = data_sample.user_name.split()[0][0:1] + "**"
        else:
            presentee_first_name = data_sample.user_name.split()[0] + "**"

        data = ObjectDict({
            "type": type,
            "successful_recommendation": self.locale.translate("referral_success"),
            "variants":
                {
                    "presentee_first_name": presentee_first_name if not in_person else data_sample.user_name,
                    "recom_name": data_sample.employee_name,
                    "company_name": data_sample.company_abbreviation,
                    "failed_position_titles": [r.data.position for r in failed_recommendations],
                    "claimed_position_titles": [r.data.position for r in claimed_recommendations],
                    "unclaimed_position_titles": [r.data.position for r in unclaimed_recommendations],
                    "valid_rkeys": valid_rkeys,
                    "new_user": data_sample.user_name[0:1] + "**" if not in_person else data_sample.user_name,
                    "apply_id": data_sample.apply_id,
                    "mobile": data_sample.mobile[0:3] + "****" + data_sample.mobile[-4:],
                    "wechat": wechat,
                    "in_person": in_person
                }
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
                "referral_record_ids": self.params.rkey.split(','),
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
                "referral_record_ids": self.params.rkey.split(','),
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
        self.params.share = yield self._make_share()
        self.redis.set(key, ObjectDict(pid=pid), ttl=60 * 60 * 24)
        reward = yield self.employee_ps.get_bind_reward(self.current_user.company.id, const.REWARD_UPLOAD_PROFILE)
        position_info = yield self.position_ps.get_position(pid)
        data = yield self.company_ps.get_only_referral_reward(self.current_user.company.id)
        reward = reward if not data.flag or (data.flag and position_info.is_referral) else 0
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


class ReferralCrucialInfoHandler(BaseHandler):
    """关键信息推荐"""

    @handle_response
    @authenticated
    @check_employee_common
    @gen.coroutine
    def get(self):
        pid = self.params.pid
        position_info = yield self.position_ps.get_position(pid)
        reward = yield self.employee_ps.get_bind_reward(self.current_user.company.id, const.REWARD_CONTACT_INFORMATION)
        data = yield self.company_ps.get_only_referral_reward(self.current_user.company.id)
        reward = reward if not data.flag or (data.flag and position_info.is_referral) else 0
        title = position_info.title

        relationship = yield self.dictionary_ps.get_referral_relationship(self.locale)
        degree = yield self.dictionary_ps.get_degrees(self.locale)
        required_fields = yield self.position_ps.get_position_required_fields(pid)
        self.params.share = yield self._make_share()
        self.render_page(template_name="employee/recom-candidate-info.html", data=ObjectDict({
            "job_title": title,
            "points": reward,
            "required_fields": required_fields,
            "consts": dict(
                relation=relationship,
                degree=degree
            )
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

        if self.params.endpoint == 'connection':
            # 保存员工推荐评价信息

            if int(self.params.referral_remark or 0) == 1:
                # 不是点击“帮我内推”button， 而是直接投递之后在推荐进度列表中进行"评价Ta"
                ret = yield self.employee_ps.nonreferral_save_evaluation(
                    self.current_user.sysuser.id,
                    self.current_user.company.id,
                    self.params, self.json_args
                )
                self.track("inDirectReferral", properties={"apply_origin": const.SA_INDIRECT_REFERRAL_TRANSFER})
            else:
                ret = yield self.employee_ps.referral_save_evaluation(
                    self.current_user.sysuser.id,
                    self.current_user.company.id,
                    self.params, self.json_args
                )
                if ret.status == const.API_SUCCESS:
                    self.track("cReferralEvaluationSuccess")
                self._add_sensor_track()
            if not ret.status == const.API_SUCCESS:
                self.send_json_error(message=ret.message)
                return

            if int(self.params.flag or 0) == const.REFERRAL_EVAL_CONTACT_MES_TMP:
                next_url = self.make_url(path.REFERRAL_PROGRESS, self.params)
            elif int(self.params.flag or 0) == const.REFERRAL_EVAL_RADAR:
                next_url = self.make_url(path.REFERRAL_RADAR, self.params)
            elif int(self.params.flag or 0) == const.REFERRAL_EVAL_RECOM_PROGRESS:
                next_url = self.make_url(path.REFERRAL_PROGRESS, self.params)
            elif int(self.params.flag or 0) == const.REFERRAL_EVAL_TEN_MIN_MES_TMP:
                next_url = self.make_url(path.EMPLOYEE_TEN_MIN_TMP, self.params)
            elif int(self.params.flag or 0) == const.REFERRAL_EVAL_SEEK_RECOM_CARDS:
                next_url = self.make_url(path.REFERRAL_RADAR_SEEK_RECOM, self.params)
            else:
                next_url = ''

            # 推荐评价红包
            # recom_record_id = self.params.get('_id')
            # position_title = yield self.redpacket_ps.get_position_title_by_recom_record_id(recom_record_id)
            # yield self.redpacket_ps.handle_red_packet_recom(
            #     recom_current_user=self.current_user,
            #     recom_record_id=recom_record_id,
            #     redislocker=self.redis,
            #     realname=self.get_argument("_realname"),
            #     position_title=position_title
            # )

            self.send_json_success(data={
                "next_url": next_url
            })
            return

        ret = yield self.employee_ps.update_referral_crucial_info(self.current_user.employee.id, self.json_args)
        self.track("directReferral", properties={"apply_origin": const.SA_DIRECT_REFERRAL_ORIGIN_REFERRAL_CRUCIAL_INFO})
        if ret.status != const.API_SUCCESS:
            self.send_json_error(message=ret.message)
            return
        else:
            self.send_json_success(data=ObjectDict({
                "rkey": ret.data
            }))
            return

    def _add_sensor_track(self):
        if int(self.params.flag or 0) == const.REFERRAL_EVAL_CONTACT_MES_TMP:
            origin = const.SA_REFERRAL_COMMENT_ORIGIN_CONTACT_MES_TMP
        elif int(self.params.flag or 0) == const.REFERRAL_EVAL_RADAR:
            origin = const.SA_REFERRAL_COMMENT_ORIGIN_RADAR
        elif int(self.params.flag or 0) == const.REFERRAL_EVAL_RECOM_PROGRESS:
            origin = const.SA_REFERRAL_COMMENT_ORIGIN_PROGRESS
        elif int(self.params.flag or 0) == const.REFERRAL_EVAL_TEN_MIN_MES_TMP:
            origin = const.SA_REFERRAL_COMMENT_ORIGIN_TEN_MIN_MES_TMP
        elif int(self.params.flag or 0) == const.REFERRAL_EVAL_SEEK_RECOM_CARDS:
            origin = const.SA_REFERRAL_COMMENT_ORIGIN_SEEK_RECOM_CARDS
        else:
            origin = const.SA_REFERRAL_COMMENT_ORIGIN_HAS_APPLY
        self.track("referralComment", properties={"comment_origin": origin})


class ReferralCommentTagsHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):
        relation_code = self.params.relation
        res = yield self.dictionary_ps.get_comment_tags_by_code(relation_code)
        self.send_json_success(data=res)


class ReferralEvaluationHandler(BaseHandler):
    """联系内推：推荐评价"""

    @handle_response
    @authenticated
    @check_employee_common
    @gen.coroutine
    def get(self):
        referral_id = self.params.referral_id
        candidate_info = None

        if int(self.params.flag or 0) == const.REFERRAL_EVAL_CONTACT_MES_TMP:
            # 新候选人通知消息模板进来 判断雷达开关，如果关闭状态则跳转到过期页面
            ret = yield self.company_ps.check_oms_switch_status(
                self.current_user.company.id,
                "人脉雷达"
            )
            if not ret.status == const.API_SUCCESS:
                self.write_error(500, message=ret.message)
                return

            switch_status = ret.data.get('valid') if ret.data else 0
            if not switch_status:
                self.render_page(
                    template_name="adjunct/msg-expired.html",
                    data={}
                )
                return

        if int(self.params.referral_remark or 0) == 1:
            # 不是点击“帮我内推”button， 而是直接投递之后在推荐进度列表中进行"评价Ta"
            ret = yield self.employee_ps.referral_contact_push(
                self.params.candidate_user_id,
                self.params.pid
            )
            if not ret.status == const.API_SUCCESS:
                self.write_error(500, message=ret.message)
                return

            presentee_name = ret.data['nickname']
            position_title = ret.data['position_name']
            pid = self.params.pid

        else:
            candidate_info = yield self.employee_ps.referral_evaluation_page_info(
                self.current_user.company.id, self.current_user.sysuser.id, referral_id)
            if not candidate_info.status == const.API_SUCCESS:
                self.write_error(500, message=candidate_info.message)
                return

            presentee_name = candidate_info.data['username']
            position_title = candidate_info.data['position_name']
            pid = candidate_info.data['position_id']

        relationship = yield self.dictionary_ps.get_referral_relationship(self.locale)
        degree = yield self.dictionary_ps.get_degrees(self.locale)
        if candidate_info and candidate_info.data['application_id'] > 0:
            # 已经做过推荐评价产生了申请
            self.render_page(template_name="employee/referral-progress.html",
                             data=dict())
        else:
            self.render_page(template_name="employee/recom-candidate-info-connect.html", data=ObjectDict({
                "job_title": position_title,
                "consts": dict(
                    relation=relationship,
                    degree=degree
                ),
                "presentee_name": presentee_name,
                "pid": pid
            }))


class ReferralResultHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """
        联系内推结果页
        :return:
        """
        self.render_page(template_name='employee/result-with-jobs.html',
                         data=dict())
