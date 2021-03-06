# coding=utf-8

"""
挖掘被动求职者相关的 Handler
"""

import enum

import tornado.gen

import conf.common as const
import conf.message as msg
from handler.base import BaseHandler
from thrift_gen.gen.common.struct.ttypes import BIZException
from util.common import ObjectDict
from util.common.decorator import authenticated
from util.tool.date_tool import curr_now_dateonly
from util.wechat.core import get_temporary_qrcode
import conf.path as path


# 基础服务 BizException 返回内容
# PASSIVE_SEEKER_NOT_START(61001, "没有操作权限，请先开启挖掘被动求职者！"),
# PASSIVE_SEEKER_SORT_USER_NOT_EXIST(61002, "未能找到用户的推荐信息，无法获取排名！"),
# PASSIVE_SEEKER_SORT_COMPANY_NOT_EXIST(61003, "无法获取公司信息，无法获取排名！"),
# PASSIVE_SEEKER_SORT_COLLEAGUE_NOT_EXIST(61004, "无法获取公司其他成员信息，无法获取排名！"),
# PASSIVE_SEEKER_RECOMMEND_PARAM_ILLEGAL(61005, "是否推荐参数不合法！"),
# PASSIVE_SEEKER_CANDIDATES_POSITION_NOT_EXIST(61006, "没有合适的职位信息！"),
# PASSIVE_SEEKER_CANDIDATES_RECORD_NOT_EXIST(61007, "没有推荐记录！"),
# PASSIVE_SEEKER_APPLY_POSITION_ALREADY_APPLY(61008, "重复申请职位！"),
# PASSIVE_SEEKER_ALREADY_APPLIED_OR_RECOMMEND(61009, "已经申请或者被推荐");
#


class RecomCustomVariableMixIn(BaseHandler):

    class IsRecomEnum(enum.Enum):
        """ candiate_recom_record.is_recom 字段含义：
        0: 推荐， 1: 未推荐（默认）， 2：忽略， 3：选择中
        """
        RECOMED = 0
        NOT_RECOMED = 1
        IGNORED = 2
        SELECTED = 3

    @tornado.gen.coroutine
    def prepare(self):
        """构建一些推荐候选人需要的相关环境变量"""

        yield super().prepare()
        yield self.refresh_recom_info()

    @tornado.gen.coroutine
    def refresh_recom_info(self):
        """构建一些推荐候选人需要的相关环境变量
        在 prepare 以及推荐后调用，保持推荐数据为最新状态
        """

        # 当前公司推荐积分配置
        reward_config = yield self.company_ps.get_company_reward_by_templateid(
            company_id=self.current_user.company.id,
            tempalte_id=const.RECRUIT_STATUS_FULL_RECOM_INFO_ID)

        # 当前员工总积分
        employee_reward = yield self.user_ps.get_employee_total_points(
            self.current_user.employee.id)

        # 当前员工获取的推荐积分总数
        hb_total = yield self.user_ps.get_employee_recommend_hb_amount(
            self.current_user.company.id,
            self.current_user.qxuser.id)

        self.employee_reward = str(employee_reward)
        self.reward_config = str(reward_config)
        self.hb_total = str(hb_total)

        # 推荐结果 message 模版，先获取自定义，在获取 default
        self._recommend_success_template = \
            self.current_user.company.conf_recommend_success or msg.DEFAULT_RECOMMEND_SUCCESS
        self._recommend_presentee_template = \
            self.current_user.company.conf_recommend_presentee or msg.DEFAULT_RECOMMEND_PRESENTEE

        self.recommend_success = self._recommend_success_template \
            .replace("{current_reward}",
                     '<span class="passive-reward">' + self.employee_reward + '</span>') \
            .replace("{recom_reward}",
                     '<span class="passive-reward">' + self.reward_config + '</span>') \
            .replace("{recom_hb}",
                     '<span class="passive-reward">' + self.hb_total + '</span>')

        self.recommend_presentee = self._recommend_presentee_template \
            .replace("{current_reward}",
                     '<span class="passive-reward">' + self.employee_reward + '</span>') \
            .replace("{recom_reward}",
                     '<span class="passive-reward">' + self.reward_config + '</span>') \
            .replace("{recom_hb}",
                     '<span class="passive-reward">' + self.hb_total + '</span>')


class RecomIgnoreHandler(RecomCustomVariableMixIn, BaseHandler):
    """跳过推荐该被动求职者
    """
    @authenticated
    @tornado.gen.coroutine
    def post(self):
        if not self.current_user.employee:
            self.write_error(416, message=msg.EMPLOYEE_NOT_BINDED_WARNING.format(self.current_user.company.conf_employee_slug))
            return

        recom_record_id = self.params.get("_id")
        click_time = self.get_argument("click_time")
        # is_recom = 2 # 暂时忽略

        recom_result = yield self.candidate_ps.post_ignore(
            recom_record_id, self.current_user.company.id,
            self.current_user.sysuser.id, click_time)

        # recom_total 推荐总数， recom_index ： 已推荐人数
        if recom_result.recom_total == (recom_result.recom_index + recom_result.recom_ignore):
            sort = yield self.candidate_ps.sorting(
                self.current_user.sysuser.id,
                self.current_user.company.id)

            if not sort:
                self.render(
                    template_name="refer/weixin/passive-seeker_v2/passive-wanting_no-more.html")
                return
            else:
                sort.hongbao = int(recom_result.recomIndex) * 2 if sort else 0

                self.render(
                    template_name="refer/weixin/passive-seeker_v2/passive-wanting_finished.html",
                    stats=sort, recommend_success=self.recommend_success)
                return

        self.render(template_name="refer/weixin/passive-seeker_v2/passive-wanting_form.html",
                    passive_seeker=recom_result,
                    recommend_presentee=self.recommend_presentee,
                    message=''
                    )


class RecomCandidateHandler(RecomCustomVariableMixIn, BaseHandler):
    """处理 recom 相关的各种 GET POST 请求"""

    @authenticated
    @tornado.gen.coroutine
    def get(self):
        # 判断是否已经绑定员工
        binded = const.YES if self.current_user.employee else const.NO

        if not binded:
            self.redirect(self.make_url(path.EMPLOYEE_VERIFY, self.params))
            return
        if not self.current_user.employee:
            self.write_error(404, message=msg.EMPLOYEE_NOT_BINDED_WARNING.format(self.current_user.company.conf_employee_slug))
            return

        id = self.params.get('id')

        if id:
            yield self._get_recom_candidate(id)
        else:
            yield self._get_recom_candidates()

    @authenticated
    @tornado.gen.coroutine
    def post(self):
        if not self.current_user.employee:
            self.write_error(404, message=msg.EMPLOYEE_NOT_BINDED_WARNING.format(self.current_user.company.conf_employee_slug))
            return

        id = self.params.get('_id')

        if id:
            yield self._post_recom_candidate(id)
        else:
            yield self._post_recom_candidates()

    @tornado.gen.coroutine
    def _get_recom_candidates(self, message=''):
        """
        入口： 挖掘被动求职者消息模板
        原十分钟推送消息模板打开页面， 现已不用该页面，跳转到过期页面
        :param message:
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
        return

    @tornado.gen.coroutine
    def _post_recom_candidates(self):
        """入口：
        从挖掘被动求职者消息模板进入，选中一个或多个被动求职者后按确认进入
        """
        ids = self.get_arguments("_ids")

        if not ids:
            yield self._get_recom_candidates('请选择推荐人！')
            return
        else:
            pass

        list_of_ids = [int(id) for id in ids]

        next_passive_seeker = yield self.candidate_ps.get_recommendations(
            self.current_user.company.id, list_of_ids)

        if next_passive_seeker:
            # 返回第一个推荐的被动求职者
            self.render(
                template_name="refer/weixin/passive-seeker_v2/passive-wanting_form.html",
                passive_seeker=next_passive_seeker,
                recommend_presentee=self.recommend_presentee,
                message=""
            )
            return
        else:
            stats = yield self.candidate_ps.sorting(
                self.current_user.sysuser.id, self.current_user.company.id)

            self.render(
                template_name="refer/weixin/passive-seeker_v2/passive-wanting_finished.html",
                stats=stats,
                recommend_success=self.recommend_success)

    @tornado.gen.coroutine
    def _get_recom_candidate(self, id):
        """从推荐TA进入，对单条推荐记录进行推荐"""

        passive_seeker = yield self.candidate_ps.get_recommendation(
            id, self.current_user.sysuser.id)

        if passive_seeker:
            # 由于是从 "推荐TA" 进入的，所以没有循环推荐的逻辑，hardcode 以下值
            passive_seeker.recom_index = 0
            passive_seeker.recom_total = 1
            passive_seeker.recom_ignore = 0
            passive_seeker.next = 1

            self.render(
                template_name="refer/weixin/passive-seeker_v2/passive-wanting_form.html",
                passive_seeker=passive_seeker,
                recommend_presentee=self.recommend_presentee,
                message=""
            )
        else:
            self.render(template_name="refer/weixin/passive-seeker_v2/passive-wanting_no-more.html")

    @tornado.gen.coroutine
    def _post_recom_candidate(self, id):
        from util.tool.str_tool import mobile_validate

        recom_record_id = id
        click_time = self.get_argument("_click_time")
        if click_time:
            click_time = click_time[:10]

        realname = self.get_argument("_realname")
        company = self.get_argument("_company")
        position = self.get_argument("_position")
        mobile = self.get_argument("_mobile")
        recom_reason = self.get_argument("_recom_reason")
        gender = self.get_argument("_gender", 0)
        email = self.get_argument("_email")

        form_items = [recom_record_id, self.current_user.sysuser.id, click_time, realname, company, position, recom_reason, email]

        self.logger.debug("post_recom_passive_seeker form_items: %s" % form_items)

        # 如果校验失败返回原页面并附加 message
        message = ''
        if any([(x == '') for x in form_items]):
            message = '有必填项未填写'

        elif mobile and not mobile_validate(mobile):
            message = '手机号格式校验失败'

        passive_seeker = ObjectDict({
            'id':             recom_record_id,
            'realname':       realname,
            'company':        company,
            'position':       position,
            'mobile':         mobile,
            'recom_reason':   recom_reason,
            'recom_index':    self.get_argument("_recom_index"),
            'presentee_name': self.get_argument("_presentee_name"),
            'position_name':  self.get_argument("_position_name"),
            'click_time':     self.get_argument("_click_time"),
            'gender':         gender,
            'email':          email,
            'next':           1,
        })

        if message:
            self.render(
                template_name='refer/weixin/passive-seeker_v2/passive-wanting_form.html',
                passive_seeker=passive_seeker,
                recommend_presentee=self.recommend_presentee,
                message=message)
            return

        try:
            recom_result = yield self.candidate_ps.post_recommend(
                self.current_user.sysuser.id,
                click_time, recom_record_id, realname, company,
                position, mobile, recom_reason,
                self.current_user.company.id, gender, email)

        except BIZException as e:
            self.render(
                template_name='refer/weixin/passive-seeker_v2/passive-wanting_form.html',
                passive_seeker=passive_seeker,
                recommend_presentee=self.recommend_presentee,
                message=e.message)
            return

        else:
            # 推荐完成以后需要重新获取一下总积分
            yield self.refresh_recom_info()

            # 已经全部推荐了
            if recom_result.recom_total == recom_result.recom_index + recom_result.recom_ignore:

                stats = yield self.candidate_ps.sorting(
                    self.current_user.sysuser.id, self.current_user.company.id)

                self.render(
                    template_name="refer/weixin/passive-seeker_v2/passive-wanting_finished.html",
                    stats=stats,
                    recommend_success=self.recommend_success)

            # 还有未推荐的
            else:
                self.render(
                    template_name="refer/weixin/passive-seeker_v2/passive-wanting_form.html",
                    passive_seeker=recom_result,
                    recommend_presentee=self.recommend_presentee,
                    message=message
                )
