# coding=utf-8
import traceback
from tornado.httputil import url_concat
from tornado import gen

import conf.platform as const_platform
import conf.common as const
import conf.message as msg
import conf.fe as fe
import conf.message as messages
import conf.path as path
import conf.sensors as sensor
from handler.base import BaseHandler
from handler.platform.user import UserSurveyConstantMixin
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated, check_employee_common, check_radar_status
from util.tool.json_tool import json_dumps
from util.tool.str_tool import to_str
from urllib import parse


class AwardsLadderPageHandler(BaseHandler):
    """Render page to employee/reward-rank.html
    包含转发信息
    """

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        # 判断是否已经绑定员工
        binded = const.YES if self.current_user.employee else const.NO

        if not binded:
            self.redirect(self.make_url(path.EMPLOYEE_VERIFY, self.params))
            return
        else:
            # 清空未读赞的数量
            yield self.employee_ps.reset_unread_praise(employee_id=self.current_user.employee.id)
            cover = self.share_url(self.current_user.company.logo)
            share_title = messages.EMPLOYEE_AWARDS_LADDER_SHARE_TEXT.format(
                self.current_user.company.abbreviation or "")
            self.params.share = ObjectDict({
                "cover": cover,
                "title": share_title,
                "description": messages.EMPLOYEE_AWARDS_LADDER_DESC_TEXT,
                "link": self.fullurl()
            })
            ladder_type = yield self.employee_ps.get_award_ladder_type(self.current_user.company.id)
            policy_link = self.make_url(path.EMPLOYEE_REFERRAL_POLICY, self.params)
            self._add_sensor_track()
            if ladder_type == 1:

                self.render_page(template_name="employee/reward-rank.html",
                                 data={"policy_link": policy_link})
            else:
                self.render_page(template_name="employee/reward-rank-dark.html",
                                 data={"policy_link": policy_link})

    def _add_sensor_track(self):
        if self.params.from_template_message == str(const.TEMPLATES.WX_RANKING_NOTICE_TO_EMPLOYEE):
            origin = const.SA_ORIGIN_RANKING_TEMPLATE
        else:
            origin = const.SA_ORIGIN_PORTAL
        self.track("cAwardLadder", properties={"origin": origin})


class AwardsLadderHandler(BaseHandler):
    """API for AwardsLadder data"""

    TIMESPAN = ('month', 'year', 'quarter')

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """
        返回员工积分排行榜数据
        """
        if self.params.rank_type not in self.TIMESPAN:
            self.send_json_error()
            return

        # 判断是否已经绑定员工
        binded = const.YES if self.current_user.employee else const.NO
        if not binded:
            self.send_json_error(
                message=messages.EMPLOYEE_NOT_BINDED_WARNING.format(self.current_user.company.conf_employee_slug))
            return

        list_only = self.params.list_only
        company_id = self.current_user.company.id
        employee_id = self.current_user.employee.id
        rank_type = self.params.rank_type  # year/month/quarter
        ladder_type = self.params.ladder_type

        page_from = (int(self.params.get("page_num", 0)) * const_platform.RANK_LIST_PAGE_COUNT)
        page_size = const_platform.RANK_LIST_PAGE_COUNT

        rank_list = yield self.employee_ps.get_award_ladder_info(
            employee_id=employee_id,
            company_id=company_id,
            type=rank_type,
            page_from=page_from,
            page_size=page_size
        )
        self.logger.debug("employee_id:{}, cpmpany_id: {},type:{}, page_from: {}, page_size{}, rank_list：{}".format(
            employee_id, company_id, rank_type, page_from, page_size, rank_list))

        type = const.LADDER_TYPE.get(rank_type)
        current_user_rank = yield self.employee_ps.get_current_user_rank_info(self.current_user.employee.id, int(type))
        rank_list = sorted(rank_list, key=lambda x: x.level)
        if ladder_type == 'normal':
            rank_list = list(filter(lambda x: x if x.level <= 3 else x.level != current_user_rank.level, rank_list))
        if list_only:
            data = ObjectDict(rank_list=rank_list)
        else:
            data = ObjectDict(employee_id=employee_id, rank_list=rank_list, current_user_rank=current_user_rank)
        self.logger.debug("awards ladder data: %s" % data)

        self.send_json_success(data=data)


class WechatSubInfoHandler(BaseHandler):
    """
    获取微信信息
    字符类型的自定义参数的格式为{场景值(大写)}_{自定义字符串}，场景值必须为大写英文字母（不包含数字、下划线、空格等特殊字符）
    int类型 scene_id规范为：32位二进制, 5位type + 27位自定义编号(比如hrid, userid)。见 https://wiki.moseeker.com/weixin.md
    """

    @handle_response
    @gen.coroutine
    def get(self):
        pattern_id = self.params.scene or 99
        str_scene = self.params.str_scene or ''  # 字符串类型的场景值
        str_code = self.params.str_code or ''  # 字符串类型的自定义参数
        scene_code = const.TEMPORARY_CODE_STR_SCENE.format(str_scene, str_code)
        if str_code and str_scene:
            wechat = yield self.wechat_ps.get_wechat_info(self.current_user, scene_id=scene_code, in_wechat=self.in_wechat, action_name="QR_STR_SCENE")
        else:
            if int(pattern_id) == const.QRCODE_POSITION and self.params.pid:
                scene_id = int('11111000000000000000000000000000', base=2) + int(self.params.pid)
            else:
                scene_id = int('11110000000000000000000000000000', base=2) + int(pattern_id)
            wechat = yield self.wechat_ps.get_wechat_info(self.current_user, scene_id=scene_id, in_wechat=self.in_wechat)
        self.send_json_success(data=wechat)
        return


class PraiseHandler(BaseHandler):
    """
    点赞操作
    """

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        praise_employee_id = self.json_args.praise_user_id
        delete = self.json_args.delete
        if delete:
            action = 'cancel_vote'
            result = yield self.employee_ps.cancel_prasie(self.current_user.employee.id, praise_employee_id)
        else:
            action = 'vote'
            result = yield self.employee_ps.vote_prasie(self.current_user.employee.id, praise_employee_id)
        if result:
            self.track(sensor.PRAISE, properties={"action": action})
            self.send_json_success()
        else:
            self.send_json_error()


class AwardsHandler(BaseHandler):
    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):

        # 判断是否已经绑定员工
        binded = const.YES if self.current_user.employee else const.NO
        email_activation_state = const.OLD_YES if binded else self.current_user.employee.activation

        if binded:
            # 获取绑定员工
            rewards_response = yield self.employee_ps.get_employee_rewards(
                employee_id=self.current_user.employee.id,
                company_id=self.current_user.company.id,
                locale=self.locale,
                page_number=int(self.params.page_number),
                page_size=int(self.params.page_size),
            )
            rewards_response.update({
                'binded': binded,
                'email_activation_state': email_activation_state
            })

            self.send_json_success(rewards_response)
            return

        else:
            self.send_json_error(
                message=messages.EMPLOYEE_NOT_BINDED_WARNING.format(self.current_user.company.conf_employee_slug))


class EmployeeUnbindHandler(BaseHandler):
    """员工解绑 API"""

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        infra_bind_status, employee = yield self.employee_ps.get_employee_info(
            self.current_user.sysuser.id,
            self.current_user.company.id
        )
        fe_bind_status = self.employee_ps.convert_bind_status_from_thrift_to_fe(infra_bind_status)

        if fe_bind_status in [fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS,
                              fe.FE_EMPLOYEE_BIND_STATUS_PENDING]:

            result, message = yield self.employee_ps.unbind(
                employee.id,
                self.current_user.company.id,
                self.current_user.sysuser.id
            )
            if result:
                self.send_json_success()
            else:
                self.send_json_error(message=message)
        else:
            self.send_json_error(message='not binded or pending')


class ResendBindEmailHandler(BaseHandler):
    """重新发送认证邮件"""

    @handle_response
    @gen.coroutine
    def post(self):
        res = yield self.employee_ps.resend_bind_email(self.current_user)
        if res.status == const.API_SUCCESS:
            self.send_json_success()
        else:
            self.send_json_error()


class EmployeeBindPageHandler(BaseHandler):
    """员工认证页面"""

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        res = yield self.employee_ps.get_employee_auth_tips_info(self.current_user)
        title = res.title_ename or const.PAGE_EN_VERIFICATION if self.locale.code == const.LOCALE_ENGLISH else \
            res.title or const.PAGE_VERIFICATION
        self.render_page(template_name="employee/bind.html", data={}, meta_title=title)


class EmployeeBindHandler(BaseHandler):
    """员工绑定 API
    /api/employee/binding"""

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        # 先获取员工认证配置信息
        conf_response = yield self.employee_ps.get_employee_conf(
            self.current_user.company.id)
        if not conf_response.exists:
            self.send_json_error("no employee conf")
            return
        else:
            pass

        # 获取员工认证页各项数据
        mate_num, reward, custom_supply_info, custom_supply_field, employee_auth_tips_info, is_valid_email = yield [
            self.employee_ps.get_mate_num(self.current_user.company.id),
            self.employee_ps.get_bind_reward(self.current_user.company.id, const.REWARD_VERIFICATION),
            self.employee_ps.get_employee_custom_info(self.current_user),
            self.employee_ps.get_employee_custom_field(self.current_user),
            self.employee_ps.get_employee_auth_tips_info(self.current_user),
            self.employee_ps.get_bind_email_is_valid(self.current_user)
        ]

        # 根据 conf 来构建 api 的返回 data
        data = yield self.employee_ps.make_binding_render_data(
            current_user=self.current_user,
            mate_num=mate_num,
            reward=reward,
            conf=conf_response.employeeVerificationConf,
            custom_supply_info=custom_supply_info,
            custom_supply_field=custom_supply_field,
            auth_tips_info=employee_auth_tips_info,
            is_valid_email=is_valid_email,
            in_wechat=self.in_wechat,
            locale=self.locale
        )

        # 是否需要弹出 隐私协议 窗口
        res_privacy, data_privacy = yield self.privacy_ps.if_privacy_agreement_window(
            self.current_user.sysuser.id)
        data.show_privacy_agreement = data_privacy

        self.send_json_success(data=data)

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        result, payload = self.employee_ps.make_bind_params(
            self.current_user.sysuser.id,
            self.current_user.company.id,
            self.json_args,
            self.params
        )

        self.logger.debug(result)
        self.logger.debug(payload)

        if not result:
            self.send_json_error(message=payload)
            return

        thrift_bind_status = yield self.employee_ps.get_employee_bind_status(
            self.current_user.sysuser.id,
            self.current_user.company.id
        )

        fe_bind_status = self.employee_ps.convert_bind_status_from_thrift_to_fe(
            thrift_bind_status)

        self.logger.debug(
            "thrift_bind_status: %s, fe_bind_status: %s" %
            (thrift_bind_status, fe_bind_status))

        # early return 1
        if fe_bind_status == fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS:
            self.send_json_error(
                message=messages.EMPLOYEE_BINDED_WARNING.format(self.current_user.company.conf_employee_slug))
            return

        result, result_message = yield self.employee_ps.bind(payload)
        self.logger.debug("bind result: {}, result_message: {}".format(result, result_message))

        # early return 2
        if not result:
            # 需要将员工两字改成员工自定义称谓
            if result_message == messages.EMPLOYEE_BINDING_FAILURE_INFRA and \
                self.current_user.company.conf_employee_slug:
                result_message = self.current_user.company.conf_employee_slug + \
                                 self.locale.translate(messages.EMPLOYEE_BINDING_FAILURE)
            elif result_message.startswith(messages.EMPLOYEE_BINDING_FAILURE_EMAIL_OCCUPIED_INFRA):
                result_message = self.locale.translate(
                    messages.EMPLOYEE_BINDING_FAILURE_EMAIL_OCCUPIED)

            self.send_json_error(message=result_message)
            return

        message = result_message

        # CatesEmployeeBindHandler 生成本参数
        if self.json_args.get('redirect_when_bind_success'):
            self.params.update(dict(
                redirect_when_bind_success=self.json_args.get('redirect_when_bind_success')
            ))

        next_url = self.params.next_url if self.params.next_url else self.make_url(path.POSITION_LIST, self.params)
        if self.params.get('redirect_when_bind_success'):
            next_url = self.make_url(path.GATES_EMPLOYEE, redirect=self.params.get('redirect_when_bind_success'))

        self.logger.debug('gates_next_url: %s' % next_url)

        self.send_json_success(
            data={'next_url': next_url},
            message=message
        )


class CatesEmployeeBindHandler(EmployeeBindHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """定制接口: gates客户要求已经认证的用户跳转到他们指定的页面
        未认证的员工跳转到认证页面
        待认证成功后再跳转到指定的页面
        """

        bind_status = yield self.employee_ps.get_employee_bind_status(
            user_id=self.current_user.sysuser.id,
            company_id=self.current_user.company.id
        )
        url = parse.unquote(self.get_argument('redirect', ''))

        if bind_status == fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS:
            if url:
                self.redirect(
                    url
                )  # 员工已经认证了则直接跳转到来也页面
        else:
            self.redirect(
                url_concat(
                    '{}://{}{}'.format(
                        self.request.protocol,
                        self.request.host,
                        '/m/app/employee/binding'
                    ),
                    dict(
                        wechat_signature=self.current_user.wechat.signature,
                        redirect_when_bind_success=parse.quote(url)
                    )
                )
            )  # 没有认证 跳转到 wechat的认证页面


class EmployeeBindEmailHandler(BaseHandler):
    @handle_response
    @gen.coroutine
    def get(self):
        activation_code = self.params.activation_code
        bind_email_source = self.params.bind_email_source or 0
        result, message, employee_id = yield self.employee_ps.activate_email(
            activation_code, bind_email_source)
        try:
            if employee_id:
                employee = yield self.user_ps.get_employee_by_id(employee_id)
                user = yield self.usercenter_ps.get_user(employee.sysuser_id) if employee.sysuser_id else ObjectDict()
                self.track("cEmployeeClickBindingEmail", distinct_id=user.data.id, is_login_id=bool(user.data.username.isdigit() if user.data and user.data.username else None))
                if result:
                    self.track("cVerifyEmailSuccess", distinct_id=user.data.id, is_login_id=bool(user.data.username.isdigit() if user.data and user.data.username else None))
        except Exception as e:
            self.logger.error("[sensor_bind_email_fail]:{}{}{}{}".format(result, message, employee_id, traceback.format_exc()))
        tparams = dict(
            qrcode_url=self.make_url(
                path.IMAGE_URL,
                self.params,
                url=self.static_url(self.current_user.wechat.qrcode)),
            wechat_name=self.current_user.wechat.name
        )
        tname = 'success' if result else 'failure'

        self.render(template_name='employee/certification-%s.html' % tname,
                    **tparams)
        if employee_id is None:
            self.logger.error(
                'employee_log_id_None   current_user:{}, result:{}, message:{}, params:{}'.format(self.current_user,
                                                                                                  result, message,
                                                                                                  self.params))


class RecommendRecordsHandler(BaseHandler):
    """员工-推荐记录"""

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        page_no = self.params.page_no or 1
        page_size = self.params.page_size or 10
        req_type = self.params.type or 1
        res = yield self.employee_ps.get_recommend_records(
            self.current_user.sysuser.id, req_type, page_no, page_size)
        self.logger.debug("RecommendrecordsHandler:{}".format(res))
        self.send_json_success(data=res)


class CustomInfoHandler(BaseHandler):
    """员工补填信息"""

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        binding_status, employee = yield self.employee_ps.get_employee_info(
            self.current_user.sysuser.id,
            self.current_user.company.id
        )

        fe_binding_status = self.employee_ps.convert_bind_status_from_thrift_to_fe(
            binding_status)

        # unbinded users may not need to know this page
        if (fe_binding_status not in [fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS,
                                      fe.FE_EMPLOYEE_BIND_STATUS_PENDING]):
            self.write_error(404)
            return
        else:
            pass

        selects = yield self.employee_ps.get_employee_custom_fields(
            self.current_user, self.locale)
        custom_field_info = yield self.employee_ps.get_employee_custom_info(self.current_user)

        data = ObjectDict(
            fields=selects,
            from_wx_template=self.params.from_wx_template or "x",
            employee_id=employee.id,
            model=custom_field_info
        )

        self.render_page(
            template_name="employee/bind_success_info.html",
            data=data)

    @handle_response
    @gen.coroutine
    def post(self):
        # 将dict转为list
        custom_field_values = []
        values = self.json_args.get("model") or {}
        [custom_field_values.append({k: v}) for k, v in values.items()]
        _, employee = yield self.employee_ps.get_employee_info(self.current_user.sysuser.id, self.current_user.company.id)
        res = yield self.employee_ps.update_employee_custom_supply_info(employee.id, self.current_user.company.id, custom_field_values)
        if res.status == const.API_SUCCESS:
            self.send_json_success(message=res.message)
        else:
            self.send_json_error(message=res.message)


class ApiEmployeeSupplyListHandler(BaseHandler):
    """获取补填信息配置列表"""

    @handle_response
    @gen.coroutine
    def get(self):
        data = yield self.employee_ps.get_employee_custom_field(self.current_user)
        self.send_json_success(data)


class ApiEmployeeSupplyInfoHandler(BaseHandler):
    """获取员工补填信息"""

    @handle_response
    @gen.coroutine
    def get(self):
        cname = self.params.cname
        custom_field = self.params.custom_field

        data = yield self.employee_ps.get_employee_supply_info_by_custom_field(cname, custom_field, self.current_user.company.id)
        self.send_json_success(data)

class ApiEmployeeRecomSubscribeHandler(BaseHandler):
    """员工职位推荐订阅设置"""

    @handle_response
    @gen.coroutine
    def post(self):
        cname = self.params.cname
        custom_field = self.params.custom_field

        data = yield self.employee_ps.get_employee_supply_info_by_custom_field(cname, custom_field, self.current_user.company.id)
        self.send_json_success(data)

class BindCustomInfoHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):

        binding_status, employee = yield self.employee_ps.get_employee_info(
            self.current_user.sysuser.id,
            self.current_user.company.id
        )

        # 判断与跳转
        self.params.pop('next_url', None)
        self.params.pop('headimg', None)
        self.params.pop('from_wx_template', None)
        next_url = self.make_url(path.POSITION_LIST, self.params, noemprecom=str(const.YES))

        if self.params.from_wx_template == "o":
            message = messages.EMPLOYEE_BINDING_CUSTOM_FIELDS_DONE.format(self.current_user.company.conf_employee_slug)
        else:
            if employee.authMethod == const.USER_EMPLOYEE_AUTH_METHOD.EMAIL:
                message = [self.locale.translate(messages.EMPLOYEE_BINDING_EMAIL_DONE0),
                           self.locale.translate(messages.EMPLOYEE_BINDING_EMAIL_DONE1)]
            else:
                message = self.current_user.company.conf_employee_slug + self.locale.translate(
                    messages.EMPLOYEE_BINDING_SUCCESS)

        self.render(
            template_name='refer/weixin/employee/employee_binding_tip_v2.html',
            result=0,
            messages=message,
            nexturl=next_url,
            source=1,
            button_text=self.locale.translate(messages.EMPLOYEE_BINDING_EMAIL_BTN_TEXT)
        )


class BindInfoHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        binding_status, employee = yield self.employee_ps.get_employee_info(
            self.current_user.sysuser.id,
            self.current_user.company.id
        )

        fe_binding_stauts = self.employee_ps.convert_bind_status_from_thrift_to_fe(
            binding_status)

        # unbinded users may not need to know this page
        if fe_binding_stauts not in [fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS, fe.FE_EMPLOYEE_BIND_STATUS_PENDING]:
            self.write_error(404)
            return

        if fe_binding_stauts == fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS and not employee.id:
            self.write_error(416)
            return

        keys = []
        for k, v in self.json_args.model.items():
            if k.startswith("key_") and v:
                confid = int(k[4:])
                keys.append({confid: [to_str(v[0: 50])]})

        self.logger.debug("keys: %s" % keys)
        custom_fields = json_dumps(keys)

        # 利用基础服务更新员工自定义补填字段，
        # 注意：对于email 认证 pending 状态的（待认证）员工，需要调用不同的基础服务接口
        if fe_binding_stauts == fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS:
            yield self.employee_ps.update_employee_custom_fields(employee.id, custom_fields)

        elif fe_binding_stauts == fe.FE_EMPLOYEE_BIND_STATUS_PENDING:
            yield self.employee_ps.update_employee_custom_fields_for_email_pending(
                self.current_user.sysuser.id, self.current_user.company.id, custom_fields)
        else:
            assert False

        next_url = self.params.next_url if self.params.next_url else self.make_url(path.POSITION_LIST, self.params)
        # 绑定成功回填自定义配置字段成功
        redirect_when_bind_success = self.json_args.get('redirect_when_bind_success') or self.get_argument(
            'redirect_when_bind_success', '')

        if binding_status == fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS and redirect_when_bind_success:
            next_url = redirect_when_bind_success

        self.params.from_wx_template = self.json_args.from_wx_template
        self.send_json_success(
            data=ObjectDict(
                next_url=next_url
            ))


class BindedHandler(BaseHandler):
    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):

        binding_status, employee = yield self.employee_ps.get_employee_info(
            self.current_user.sysuser.id,
            self.current_user.company.id
        )

        # unbinded users may not need to know this page
        fe_bind_status = self.employee_ps.convert_bind_status_from_thrift_to_fe(
            binding_status)

        if (fe_bind_status not in [fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS,
                                   fe.FE_EMPLOYEE_BIND_STATUS_PENDING]):
            self.logger.debug(
                "sysuser_id: %s, company_id: %s" % (self.current_user.sysuser.id, self.current_user.company.id))
            self.logger.debug("该员工未绑定，也不是pending状态")
            self.write_error(404)
            return

        else:
            if fe_bind_status == fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS:
                message = self.current_user.company.conf_employee_slug + self.locale.translate(
                    messages.EMPLOYEE_BINDING_SUCCESS)
            else:
                message = [self.locale.translate(messages.EMPLOYEE_BINDING_EMAIL_DONE0),
                           self.locale.translate(messages.EMPLOYEE_BINDING_EMAIL_DONE1)]

            self.render(
                template_name='refer/weixin/employee/employee_binding_tip_v2.html',
                result=0,
                messages=message,
                nexturl=self.make_url(path.POSITION_LIST, self.params,
                                      noemprecom=str(const.YES)),
                button_text=messages.EMPLOYEE_BINDING_DEFAULT_BTN_TEXT
            )


class EmployeeReferralPolicyHandler(BaseHandler):
    """
    员工内推政策
    https://git.moseeker.com/doc/complete-guide/blob/feature/v0.1.0/develop_docs/referral/frontend/wechat_v0.1.0.md
    https://git.moseeker.com/doc/complete-guide/blob/feature/v0.1.0/develop_docs/referral/basic_service/%E5%86%85%E6%8E%A8v0.1.0-api.md
    """

    @authenticated
    @handle_response
    @gen.coroutine
    def get(self):
        # 判断是否已经绑定员工
        binded = const.YES if self.current_user.employee else const.NO

        if not binded:
            self.redirect(self.make_url(path.EMPLOYEE_VERIFY, self.params))
            return
        result, data = yield self.employee_ps.get_referral_policy(self.current_user.company.id)

        scene_id = int('11110000000000000000000000000000', base=2) + int(const.QRCODE_POLICY)
        wechat = yield self.wechat_ps.get_wechat_info(
            self.current_user,
            scene_id=scene_id,
            in_wechat=self.in_wechat
        )
        if result and data and data.get("priority"):
            link = data.get("link", "")
            if link:
                self.redirect(parse.unquote(link))
                return
            else:
                data = ObjectDict({
                    "fulltext": data.get("text"),
                    "wechat": wechat
                })
                self.render_page(template_name="employee/referral-policy-article.html",
                                 data=data,
                                 meta_title=self.locale.translate("company_referral_policy"))
        else:
            self.render_page(template_name="employee/referral-no-article.html",
                             data={"wechat": wechat},
                             meta_title=self.locale.translate("company_referral_policy"))


class EmployeeInterestReferralPolicyHandler(BaseHandler):
    """
    员工感兴趣内推政策
    """

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        params = ObjectDict({
            "company_id": self.current_user.company.id,
            "user_id": self.current_user.sysuser.id
        })
        yield self.employee_ps.create_interest_policy_count(params)
        self.send_json_success()


class EmployeeSurveyHandler(UserSurveyConstantMixin, BaseHandler):
    """
    AI推荐项目, 员工认证调查问卷
    """

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """
        前端需要的数据结构
        {
          data: {
            constant: {
              // 部门
              department: [
                // 第一个元素是显示的文本，第二个元素是值.
                // 如果后端认为值的格式应该是“前端”这样的，可以直接改，前端都可以。
                [ "前端", 1 ],
                [ "产品", 2 ],
              ],
              // 职级
              job_grade: [
                [ "总监", 1 ],
                [ "经理", 2 ],
                // ...
              ],
              // 学历
              degree: [
                [ "小学", 1 ],
                [ "高中", 2 ],
              ]
            },

            // 用于回显表单。
            model: {
              department: 1,
              job_grade: 2,
              degree: 1,
              city: "上海",
              city_code: 112,
              position: "前端开发"
            }
          }
        }
        :return:
        """
        if not self.current_user.employee:
            self.write_error(http_code=401, message="您不是员工")
            return

        teams = yield self._get_teams()  # 获取公司下部门
        job_grade = self._get_job_grade()  # 获取职级
        degree = yield self._get_degree()  # 获取学历
        survey_info = yield self._get_employee_survey_info()

        page_data = {
            "constant": {
                "department": teams,
                "job_grade": job_grade,
                "degree": degree
            },
            "model": survey_info
        }

        self.render_page(
            template_name="adjunct/employee-survey.html",
            data=page_data,
            meta_title=const.PAGE_AI_EMPLOYEE_SURVEY)

    @gen.coroutine
    def _get_teams(self):
        teams = yield self.employee_ps.get_employee_company_teams(self.current_user.company.id)
        return [[t["name"], t["id"]] for t in teams]

    def _get_job_grade(self):
        return self.listify_dict(self.constant.job_grade)

    @gen.coroutine
    def _get_degree(self):
        degree_dict = yield self.dictionary_ps.get_degrees()
        return [[name, int(str_code)] for str_code, name in degree_dict.items()]

    @gen.coroutine
    def _get_employee_survey_info(self):
        """
        获取更改员工(用户)提交过的调查问卷填写数据
        :return:
        """
        employee_survey_info = yield self.employee_ps.get_employee_survey_info(self.current_user)
        return employee_survey_info


class APIEmployeeSurveyHandler(BaseHandler):
    """
    AI推荐项目, 员工认证调查问卷
    """

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        survey = ObjectDict(self.json_args.model)

        must_have = {"department", "job_grade", "degree", "city", "city_code", "position"}
        assert must_have.issubset(survey.keys())

        res = yield self.employee_ps.post_employee_survey_info(self.current_user.employee, survey)
        if res.status == const.API_SUCCESS:
            self.send_json_success()
        else:
            self.send_json_error()


class EmployeeAiRecomHandler(BaseHandler):
    """
    AI推荐项目, 员工推荐职位列表, 功能:
    1. 展示本次员工推荐职位
    2. 带红包功能
        1) 红包样式
        2) 转发功能
    3. 需要对职位列表做出改造
    """

    RECOM_AUDIENCE_EMPLOYEE = 2

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self, recom_push_id):
        recom_push_id = int(recom_push_id)
        recom_audience = self.RECOM_AUDIENCE_EMPLOYEE
        recom = self.position_ps._make_recom(self.current_user.sysuser.id)
        self.params.share = yield self.get_employee_recom_share_info(recom_push_id, recom)

        self.render_page("adjunct/job-recom-list.html",
                         data={"recomAudience": recom_audience,
                               "recomPushId": recom_push_id,
                               "recom": recom})

    @gen.coroutine
    def get_employee_recom_share_info(self, recom_push_id, recom):
        """
        !重要!
        分享信息
        """
        escape = [
            "pid", "keywords", "cities", "candidate_source",
            "employment_type", "salary", "department", "occupations",
            "custom", "degree", "page_from", "page_size"
        ]

        link = self.make_url(
            path.POSITION_LIST,
            self.params,
            recom=recom,
            recom_push_id=recom_push_id,
            from_employee_ai_recom=1,
            escape=escape)

        company_info = yield self.company_ps.get_company(
            conds={"id": self.current_user.company.id}, need_conf=True)

        cover = self.share_url(company_info.logo)
        title = company_info.abbreviation + self.locale.translate('job_hotjobs')
        description = self.locale.translate(msg.SHARE_DES_DEFAULT)

        share_info = ObjectDict({
            "cover": cover,
            "title": title,
            "description": description,
            "link": link
        })

        return share_info


class EmployeeReferralCardsHandler(BaseHandler):
    """
    十分钟消息推送卡片
    """

    @handle_response
    @authenticated
    @check_employee_common
    @gen.coroutine
    def get(self):
        """
        获取卡片信息
        params:
        send_timestamp: 发送消息模板的时间
        page_size: 分页获取卡片数据
        page_number: 页码
        :return:
        {
            "status": 0,
            "message": "success",
            "data": {
                "cards":[
                    {
                        user_id: 123, // 用户id.
                        nickname: 'panlingling', // 微信昵称
                        avatar: 'http://url', // 用户头像.
                        pv: 2, // 浏览职位的次数.
                        position_name: '职位名称',
                        degree: 1, // 几度.
                        pid: 123, // 职位id.
                        referral_id: 123, // 内推编号
                        type: 0, // 0 邀请投递 1 推荐TA
                        from_wx_group: 0, // 转发是否来自微信群 0 否 1 是
                        chain: [
                          {
                            user_id: 12345
                            nickname: '牛牛',
                            avatar: '',
                          },
                          // ...
                        ]
                    }
                    ....
                ]
            }
        }
        """
        ret = yield self.employee_ps.get_referral_cards(
            self.current_user.sysuser.id,
            self.params.send_time,
            int(self.params.page_number or 0),
            int(self.params.page_size or 10),
            self.current_user.company.id
        )
        if not ret.status == const.API_SUCCESS:
            self.send_json_error(message=ret.message)
            return

        cards = list()
        for card_infra in ret.data:
            card = ObjectDict({
                "user_id": card_infra.get('user', {}).get('uid', 0),
                "nickname": card_infra.get('user', {}).get('nickname', ''),
                "avatar": card_infra.get('user', {}).get('avatar', ''),
                "pv": card_infra.get('position', {}).get('pv', 0),
                "position_name": card_infra.get('position', {}).get('title', ''),
                "degree": card_infra.get('user', {}).get('degree', 0),
                "pid": card_infra.get('position', {}).get('pid', 0),
                "forward_from": card_infra.get('recom', {}).get('nickname', ''),
                "referral_id": card_infra.get('recom', {}).get('referral_id', 0),
                "type": card_infra.get('recom', {}).get('type', 0),
                "from_wx_group": card_infra.get('recom', {}).get('from_wx_group', 0),
                "chain": card_infra.get('chain')
            })
            cards.append(card)
        self.send_json_success({'cards': cards})


class EmployeeReferralPassCardsHandler(BaseHandler):

    @handle_response
    @authenticated
    @check_employee_common
    @gen.coroutine
    def post(self):
        """
        十分钟消息模板： 我不熟悉
        :return:
        """
        ret = yield self.employee_ps.pass_referral_card(
            pid=self.json_args.pid,
            user_id=self.current_user.sysuser.id,
            company_id=self.current_user.company.id,
            card_user_id=self.json_args.candidate_user_id,
            timestamp=self.params.send_time)

        if ret.status == const.API_SUCCESS:
            self.send_json_success()
        else:
            self.send_json_error(message=ret.message)


class EmployeeReferralInviteApplyHandler(BaseHandler):

    @handle_response
    @authenticated
    @check_employee_common
    @gen.coroutine
    def post(self):
        """
        邀请投递
        params:
        {
            "pid": 1234    # 职位id
            "candidate_user_id" : 3456   # 被邀请的候选人user_id
            "send_timestamp": 1544404667484    # Optional  只有入口3（十分钟消息推送卡片）需要该参数
        }
        :return:
        {
            "data":{
              notified: 0, // 是否已通知候选人（消息模板通知）
              degree: 1,  // 几度人脉.
              chain_id: 123,   //  人脉连连看链路id  可能没有， 没有就是0
              // 2度及3度人脉显示人脉连连看入口
              chain: [
                {
                  uid: 123,
                  avatar: '//image.url.com',
                }
              ]
            }
        }
        """
        ret = yield self.employee_ps.invite_cards_user_apply(
            pid=self.json_args.pid,
            user_id=self.current_user.sysuser.id,
            company_id=self.current_user.company.id,
            card_user_id=self.json_args.candidate_user_id,
            # timestamp=self.json_args.get('send_timestamp') or 0)
            timestamp=self.params.send_time)

        if ret.status == const.API_SUCCESS:
            data = ObjectDict({
                "notified": ret.data['notified'],
                "degree": ret.data['degree'],
                "chain_id": ret.data['chain_id'],
                "chain": [{"uid": item['uid'], "avatar": item['avatar']} for item in ret.data['chain']]
            })
            self.send_json_success(data)
        else:
            self.send_json_error(message=ret.message)


class EmployeeReferralInvitedHandler(BaseHandler):

    @handle_response
    @authenticated
    @check_employee_common
    @gen.coroutine
    def post(self):
        """
        邀请投递候选人不在线时，员工点击“人脉连连看”或“转发邀请”时才算已处理过该候选人
        params:
        {
            "pid": 1234    # 职位id
            "user_id" : 3456   # 被邀请的候选人user_id
            "timestamp": 234234   # 10分钟消息模板入口： 消息模板链接上的参数
            "state": 1  #  1 邀请投递 3 推荐Ta
        }
        """
        ret = yield self.employee_ps.invite_cards_invited(
            user_id=self.current_user.sysuser.id,
            candidate_user_id=self.json_args.user_id,
            pid=self.json_args.pid,
            company_id=self.current_user.company.id,
            timestamp=self.json_args.send_time or '',
            state=self.json_args.state
        )

        if ret.status == const.API_SUCCESS:
            self.send_json_success()
        else:
            self.send_json_error(message=ret.message)


class EmployeeReferralConnectionHandler(BaseHandler):

    @handle_response
    @authenticated
    @check_radar_status
    @gen.coroutine
    def get(self, chain_id):
        """
        人脉连连看页面
        :param chain_id: 人脉连连看链路id
        :return:
        """
        pid = self.params.pid
        if not (pid and chain_id):
            self.write_error(500, message='pid和chain_id是必传参数')
            return

        if self.current_user.recom:
            recom_user_id = self.current_user.recom.id
        else:
            recom_user_id = self.current_user.sysuser.id

            # 为连连看最后一个目标用户打开职位详情页时显示员工信息做准备
            self.params.root_recom = self.position_ps._make_recom(self.current_user.sysuser.id)

        click_user_id = self.current_user.sysuser.id

        parent_connection_id = self.params.parent_connection_id if self.params.parent_connection_id else 0
        ret_conn = yield self.employee_ps.referral_connections(
            self.current_user.company.id, recom_user_id, click_user_id, chain_id, pid, parent_connection_id)
        if not ret_conn.status == const.API_SUCCESS:
            self.write_error(500, message=ret_conn.message)
            return

        parent_connection_id = ret_conn.data['parent_id'] if ret_conn.data.get('parent_id') else 0
        self.params.parent_connection_id = parent_connection_id
        page_data = {
            "pid": ret_conn.data['pid'],
            "current_uid": self.current_user.sysuser.id,
            "enable_viewer": ret_conn.data['enable_viewer'],
            "chain": ret_conn.data['chain']
        }

        end_user_nickname = ret_conn.data['chain'][-1]['nickname']
        yield self._make_share_info(chain_id, end_user_nickname)

        self.render_page(
            template_name='employee/people-hub-path.html',
            data=page_data
        )

    @gen.coroutine
    def _make_share_info(self, chain_id, end_user_nickname):
        """构建 share 内容"""

        company_info = yield self.company_ps.get_company(
            conds={"id": self.current_user.company.id}, need_conf=True)

        cover = self.share_url(company_info.logo)
        title = msg.REFERRAL_CONNECTION_TITLE
        description = msg.REFERRAL_CONNECTION_TEXT.format(end_user_nickname)

        link = self.make_url(
            path.REFERRAL_CONNECTIONS.format(chain_id),
            self.params,
            recom=self.position_ps._make_recom(self.current_user.sysuser.id),
            invite_apply=1
        )

        self.params.share = ObjectDict({
            "cover": cover,
            "title": title,
            "description": description,
            "link": link,
        })


class ReferralInviteApplyHandler(BaseHandler):

    @handle_response
    @authenticated
    @check_employee_common
    @check_radar_status
    @gen.coroutine
    def get(self):
        """
        邀请投递入口三，渲染前端页面
        :return:
        """
        yield self._make_share_info()
        self.render_page(template_name='employee/candidate-filter.html',
                         data=dict(
                             recom=self.position_ps._make_recom(self.current_user.sysuser.id)
                         ))

    @gen.coroutine
    def _make_share_info(self):
        """构建 share 内容"""

        company_info = yield self.company_ps.get_company(
            conds={"id": self.current_user.company.id}, need_conf=True)

        cover = self.share_url(company_info.logo)
        title = msg.REFERRAL_INVITE_TITLE
        description = msg.REFERRAL_INVITE_TEXT

        link = self.make_url(
            path.REFERRAL_INVITE_APPLY,
            self.params,
            recom=self.position_ps._make_recom(self.current_user.sysuser.id),
        )

        self.params.share = ObjectDict({
            "cover": cover,
            "title": title,
            "description": description,
            "link": link,
        })


class ReferralProgressHandler(BaseHandler):

    @handle_response
    @authenticated
    @check_employee_common
    @gen.coroutine
    def get(self):
        """
        员工中心 推荐进度列表页面
        :return:
        """
        yield self._make_share_info()
        self.render_page(template_name='employee/referral-progress.html',
                         data=dict())

    @gen.coroutine
    def _make_share_info(self):
        """构建 share 内容"""

        company_info = yield self.company_ps.get_company(
            conds={"id": self.current_user.company.id}, need_conf=True)

        cover = self.share_url(company_info.logo)
        title = msg.REFERRAL_PROGRESS_TITLE
        description = msg.REFERRAL_PROGRESS_DESCRIPTION

        link = self.make_url(
            path.REFERRAL_PROGRESS,
            self.params,
        )

        self.params.share = ObjectDict({
            "cover": cover,
            "title": title,
            "description": description,
            "link": link,
        })


class ReferralProgressListHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """
        员工中心 推荐进度列表页数据获取
        可根据候选人姓名 进度筛选
　　　　progress: 0全部 1被推荐人投递简历 10通过初筛  12通过面试 3内推入职 4遗憾淘汰
        :return:
        """
        params = ObjectDict({
            "user_id": self.current_user.sysuser.id,
            "company_id": self.current_user.company.id,
            "keyword": self.params.keyword or '',
            "page_size": self.params.page_size,
            "page_num": self.params.page_no,
            "progress": self.params.category
        })
        recom = self.position_ps._make_recom(self.current_user.sysuser.id)
        data = yield self.employee_ps.get_referral_progress(recom, params)

        self.send_json_success(data=data)


class ReferralProgressListSearchHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """
        员工中心 推荐进度列表页根据姓名搜索候选人
　　　　progress: 0全部 1被推荐人投递简历 10通过初筛  12通过面试 3内推入职 4遗憾淘汰
        :return:
        """
        params = ObjectDict({
            "user_id": self.current_user.sysuser.id,
            "company_id": self.current_user.company.id,
            "keyword": self.params.keyword or '',
            "progress": self.params.category or 0
        })
        ret = yield self.employee_ps.get_referral_progress_keyword(params)
        if not ret.status == const.API_SUCCESS:
            self.send_json_error(message=ret.message)
            return

        self.send_json_success(data={'list': ret.data})


class ReferralProgressDetailHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """
        员工中心 推荐进度 分享内推进度页面
        :return:
        """
        apply_id = self.params.apply_id

        params = ObjectDict({
            "user_id": self.params.candidate_user_id,
            "presentee_user_id": self.current_user.sysuser.id,
            "company_id": self.current_user.company.id,
            "progress": self.params.progress or 0,
        })

        ret = yield self.employee_ps.get_referral_progress_detail(apply_id, params)
        if not ret.status == const.API_SUCCESS:
            self.write_error(500, message=ret.message)
            return

        render_data = {
            "abnormal": ret.data['abnormal'],
            "avatar": ret.data.get('avatar', ''),
            "uid": self.params.candidate_user_id,
            "name": ret.data.get('name', ''),
            "position_name": ret.data.get('title', ''),
            "encourage": self.locale.translate(const.REFERRAL_ENCOURAGE.get(ret.data.get('encourage', ''))),
        }
        progress = list()
        for pro in ret.data.get('progress', []):
            progress.append({
                "progress_status": pro.get('progress_status', 0),
                "progress_pass": pro.get('progress_pass', 0),
                "datetime": pro.get('datetime', '')
            })

        yield self._make_share_info()
        render_data.update({"progress": progress})
        self.render_page(template_name='employee/referral-progress-detail.html',
                         data=render_data)

    @gen.coroutine
    def _make_share_info(self):
        """构建 share 内容"""

        company_info = yield self.company_ps.get_company(
            conds={"id": self.current_user.company.id}, need_conf=True)

        cover = self.share_url(company_info.logo)
        title = msg.REFERRAL_PROGRESS_TITLE
        description = msg.REFERRAL_PROGRESS_DESCRIPTION

        link = self.make_url(
            path.REFERRAL_PROGRESS_DETAIL,
            self.params,
            recom=self.position_ps._make_recom(self.current_user.sysuser.id),
        )

        self.params.share = ObjectDict({
            "cover": cover,
            "title": title,
            "description": description,
            "link": link,
        })


class ReferralRadarPageHandler(BaseHandler):

    @handle_response
    @authenticated
    @check_employee_common
    @check_radar_status
    @gen.coroutine
    def get(self):
        """
        员工中心 人脉雷达页面
        """
        ret = yield self.employee_ps.get_radar_top_data(self.current_user.sysuser.id,
                                                        self.current_user.company.id)
        if not ret.status == const.API_SUCCESS:
            self.write_error(500, message=ret.message)
            return

        yield self._make_share_info()

        self.render_page(template_name='employee/people-radar.html',
                         data={
                             "job_uv": ret.data.get('link_viewed_count'),
                             "seek_recom_uv": ret.data.get('interested_count'),
                             "recom": self.position_ps._make_recom(self.current_user.sysuser.id)
                         })

    @gen.coroutine
    def _make_share_info(self):
        """构建 share 内容"""

        company_info = yield self.company_ps.get_company(
            conds={"id": self.current_user.company.id}, need_conf=True)

        cover = self.share_url(company_info.logo)

        self.params.share = ObjectDict({
            "cover": cover,
            "title": '',  # 前端控制
            "description": '',  # 前端控制
            "link": '',  # 前端控制
        })


class ReferralRadarHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """
        员工中心 人脉雷达页面 人脉数据获取
        """
        ret = yield self.employee_ps.get_radar_data(
            self.current_user.sysuser.id,
            self.params.page_size,
            self.params.page_no,
            self.current_user.company.id
        )
        if not ret.status == const.API_SUCCESS:
            self.send_json_error(message=ret.message)
            return

        self.send_json_success(data={
            "list": ret.data['user_list'],
            "total": ret.data['total_count']
        })


class ReferralRadarCardJobViewHandler(BaseHandler):

    @handle_response
    @authenticated
    @check_employee_common
    @check_radar_status
    @gen.coroutine
    def get(self):
        """
        雷达页面 分类统计卡 职位浏览页面
        :return:
        """
        self.render_page(template_name='employee/recom-stat-jobview.html',
                         data={
                             "recom": self.position_ps._make_recom(self.current_user.sysuser.id)
                         })


class ReferralRadarCardPositionHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """
        雷达页面 分类统计卡 职位浏览统计数据
        params:
        :keyword:  按职位名搜索
        order: "time"   // 排序规则 默认 time,浏览 view 关系 depth
        :return:
        """
        data = yield self.employee_ps.radar_card_position(
            self.current_user.sysuser.id,
            self.current_user.company.id,
            self.params.keyword or '',
            self.params.order or 'time',
            self.params.page_no or 1,
            self.params.page_size or 10
        )
        self.send_json_success(data={"list": data})


class ReferralRadarCardSeekRecomHandler(BaseHandler):

    @handle_response
    @authenticated
    @check_employee_common
    @check_radar_status
    @gen.coroutine
    def get(self):
        """
        雷达页面 分类统计卡 求推荐页面
        :return:
        """
        self.render_page(template_name='employee/recom-stat-seekrecom.html',
                         data={
                             "recom": self.position_ps._make_recom(self.current_user.sysuser.id)
                         })


class ReferralRadarCardRecomHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """
        雷达页面 分类统计卡 求推荐页面数据
        :return:
        """
        data = yield self.employee_ps.radar_card_seek_recom(
            self.current_user.sysuser.id,
            self.current_user.company.id,
            self.params.page_no or 1,
            self.params.page_size or 10
        )
        self.send_json_success(data={"list": data})


class ReferralExpiredPageHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        """
        雷达模块关闭时，打开雷达相关页面跳转到该消息过期页面
        :return:
        """
        self.render_page(
            template_name="adjunct/msg-expired.html",
            data={
                'button': {
                    'text': self.locale.translate(const.REFERRAL_EXPIRED_MESSAGE),
                    'link': self.make_url(
                        path.REFERRAL_PROGRESS,
                        self.params)
                }
            })
