# coding=utf-8

from tornado.httputil import url_concat
from tornado import gen

import conf.common as const
import conf.message as msg
import conf.fe as fe
import conf.message as messages
import conf.path as path
from handler.base import BaseHandler
from handler.platform.user import UserSurveyConstantMixin
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated
from util.tool.json_tool import json_dumps
from util.tool.str_tool import to_str
from urllib import parse
import conf.platform as const_platform
from util.wechat.core import get_temporary_qrcode


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
            if ladder_type == 1:

                self.render_page(template_name="employee/reward-rank.html",
                                 data={"policy_link": policy_link})
            else:
                self.render_page(template_name="employee/reward-rank-dark.html",
                                 data={"policy_link": policy_link})


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
        if list_only:
            data = ObjectDict(rank_list=rank_list)
        else:
            data = ObjectDict(employee_id=employee_id, rank_list=rank_list, current_user_rank=current_user_rank)
        self.logger.debug("awards ladder data: %s" % data)

        self.send_json_success(data=data)


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
            result = yield self.employee_ps.cancel_prasie(self.current_user.employee.id, praise_employee_id)
        else:
            result = yield self.employee_ps.vote_prasie(self.current_user.employee.id, praise_employee_id)
        if result:
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
        mate_num = yield self.employee_ps.get_mate_num(self.current_user.company.id)
        rewards_response = yield self.employee_ps.get_bind_rewards(self.current_user.company.id)
        reward = 5
        for r in rewards_response:
            if r.get("statusName") == "完成员工认证":
                reward = r.get("points")

        # 根据 conf 来构建 api 的返回 data
        data = yield self.employee_ps.make_binding_render_data(
            self.current_user, mate_num, reward, conf_response.employeeVerificationConf)
        self.send_json_success(data=data)

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        result, payload = self.employee_ps.make_bind_params(
            self.current_user.sysuser.id,
            self.current_user.company.id,
            self.json_args)

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
        self.logger.debug("绑定成功")

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

        custom_fields = yield self.employee_ps.get_employee_custom_fields(self.current_user.company.id)

        # 处理员工认证红包
        yield self.redpacket_ps.handle_red_packet_employee_verification(
            user_id=self.current_user.sysuser.id,
            company_id=self.current_user.company.id,
            redislocker=self.redis
        )

        if custom_fields:
            next_url = self.make_url(path.EMPLOYEE_CUSTOMINFO, self.params, from_wx_template='x')
            custom_fields = True
        else:
            next_url = self.make_url(path.POSITION_LIST, self.params)
            custom_fields = False


        self.send_json_success(
            data={'next_url': next_url,
                  'custom_fields': custom_fields},
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
        url = self.get_argument('redirect', '')

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
                        redirect_when_bind_success=url
                    )
                )
            )  # 没有认证 跳转到 wechat的认证页面


class EmployeeBindEmailHandler(BaseHandler):
    @handle_response
    @gen.coroutine
    def get(self):
        activation_code = self.params.activation_code
        result, message, employee_id = yield self.employee_ps.activate_email(
            activation_code)

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
        employee = yield self.user_ps.get_employee_by_id(employee_id)

        if result and employee:
            # 处理员工认证红包开始
            yield self.redpacket_ps.handle_red_packet_employee_verification(
                user_id=employee.sysuser_id,
                company_id=employee.company_id,
                redislocker=self.redis
            )
            # 处理员工认证红包结束


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
            self.current_user.company.id)

        data = ObjectDict(
            fields=selects,
            from_wx_template=self.params.from_wx_template or "x",
            employee_id=employee.id,
            model={}
        )

        self.render_page(
            template_name="employee/bind_success_info.html",
            data=data)


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

        if fe_binding_stauts == fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS and \
            (employee.id != self.json_args._employeeid or not self.json_args._employeeid):
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

        # 绑定成功回填自定义配置字段成功
        redirect_when_bind_success = self.json_args.get('redirect_when_bind_success') or self.get_argument(
            'redirect_when_bind_success', '')

        next_url = redirect_when_bind_success or self.make_url(path.EMPLOYEE_CUSTOMINFO_BINDED, self.params)
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

    @handle_response
    @gen.coroutine
    def get(self):
        result, data = yield self.employee_ps.get_referral_policy(self.current_user.company.id)
        wechat = ObjectDict()
        wechat.subscribed = True if self.current_user.wxuser.is_subscribe else False
        wechat.qrcode = yield get_temporary_qrcode(access_token=self.current_user.wechat.access_token, pattern_id=2)
        wechat.name = self.current_user.wechat.name
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
                self.render_page(template_name="employee/referral-policy-article.html", data=data)
        else:
            self.render_page(template_name="employee/referral-no-article.html", data={"wechat": wechat})


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
