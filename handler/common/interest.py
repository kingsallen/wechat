# coding=utf-8

import traceback
from tornado import gen
from schematics.validate import DataError

import conf.path as path
import conf.common as const
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated
from util.wechat.template import favposition_notice_to_applier_tpl, favposition_notice_to_hr_tpl

from domain.user import InterestCurrentInfoForm


class UserCurrentInfoHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """ 返回用户填写的现在公司和现在职位接口

        此接口有两个用处：
        1. full参数为1，返回用户填写过的[ 姓名, 公司, 职位 ]信息给前端用.
        2. full参数为0，返回一个Boolean值，判断用户先前是否填过这些信息.

        full 参数用以判断只要返回 bool 就好了还是需要详细的数据
        """

        has_current_work = False

        has_profile, profile = yield self.profile_ps.has_profile(
            self.current_user.sysuser.id)

        if not has_profile:
            data = const.NO
            self.send_json_success(data=data)

        else:
            workexps = profile.workexps
            has_current_work = bool([w for w in workexps if w.get('end_until_now')])

            data = const.YES if has_current_work else const.NO
            self.send_json_success(data=data)

        # 处理感兴趣
        if self.params.isfav:
            yield self._opt_fav_position(has_current_work)

    @gen.coroutine
    def _opt_fav_position(self, has_info):
        """处理感兴趣后的业务逻辑"""

        if self.params.pid:
            # 1.添加感兴趣记录
            result, _ = yield self.user_ps.add_user_fav_position(
                int(self.params.pid),
                self.current_user.sysuser.id,
                const.FAV_INTEREST,
                self.current_user.sysuser.mobile,
                self.current_user.recom.id if self.params.recom else 0)

            position_info = yield self.position_ps.get_position(self.params.pid, display_locale=self.get_current_locale())

            # 2.添加定时任务，若2小时候，没有完善则发送消息模板
            # real_company_id = yield self.company_ps.get_real_company_id(
            #     position_info.publisher, position_info.company_id)
            # company_info = yield self.company_ps.get_company(
            #     conds={"id": real_company_id}, need_conf=False)
            #
            # link = self.make_url(
            #     path.COLLECT_USERINFO, pid=self.params.pid, source="wx", # 用户前端判断来源
            #     wechat_signature=self.current_user.wechat.signature)
            #
            # if not has_info:
            #     yield favposition_notice_to_applier_tpl(
            #         self.current_user.wechat.company_id,
            #         position_info,
            #         company_info.name,
            #         self.current_user.sysuser.id,
            #         link)

            # 3.添加候选人相关记录
            yield self.candidate_ps.send_candidate_interested(self.current_user.sysuser.id, self.params.pid, 1)

            # 4.向 HR 发送消息模板提示
            if position_info.publisher and result and self.current_user.sysuser.mobile:
                hr_account, hr_wx_user = yield self.position_ps.get_hr_info(
                    position_info.publisher)

                if hr_wx_user:
                    # 4. 向 HR 发送消息模板
                    yield favposition_notice_to_hr_tpl(
                        self.settings.helper_wechat_id,
                        hr_wx_user.openid,
                        position_info.title,
                        self.current_user.sysuser.name or self.current_user.sysuser.nickname,
                        self.current_user.sysuser.mobile)
                    return True

        return False


class UserCurrentUpdateHandler(BaseHandler):

    # @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """更新用户现在公司和现在职位接口
        调整为 get 方式，原因：更新用户信息，需要用户验证手机号，
        此时可能会触发帐号合并，合并完帐号后，需要重新微信 oauth，post 请求无法 oauth
        """

        if not (self.params.name and self.params.company and
                self.params.position and self.params.start_date):
            self.send_json_error(message="输入不正确，请重新输入")
            return

        form = InterestCurrentInfoForm({
            'name': self.params.name,
            'company': self.params.company,
            'position': self.params.position,
            'start_date': self.params.start_date
        })

        try:
            form.validate()
        except DataError:
            self.logger.warn(traceback.format_exc())
            self.send_json_error(message="输入不正确，请重新输入")
            return

        has_profile, profile = yield self.profile_ps.has_profile(
            self.current_user.sysuser.id)

        # 初始化 profile_id
        profile_id = None
        if has_profile:
            profile_id = profile.get("profile", {}).get("id")

        else:
            # 还不存在 profile， 创建 profile
            # 进入自定义简历创建 profile 逻辑的话，来源必定是企业号（我要投递）

            source = None
            if self.is_platform:
                source = const.PROFILE_SOURCE_PLATFORM_INTEREST
            elif self.is_qx:
                source = const.PROFILE_SOURCE_QX_INTEREST

            assert source

            result, data = yield self.profile_ps.create_profile(
                self.current_user.sysuser.id,
                source=source)

            if not result:
                raise RuntimeError('profile creation error')
            profile_id = data
            self._log_customs.update(new_profile=const.YES)

            # 创建 profile_basic
            result, data = yield self.profile_ps.create_profile_basic({}, profile_id, mode='c')

            if result:
                self.logger.debug("profile basic created, id: %s" % data)
            else:
                self.logger.error(
                    "profile_basic creation failed, res: %s" % data)

        # 创建一条工作信息
        assert profile_id
        record = ObjectDict({
            'profile_id': profile_id,
            'company_name': form.company,
            'start_date': form.start_date,
            'job': form.position,
            'end_until_now': 1
        })
        position_info = yield self.position_ps.get_position(self.params.pid)
        ret = yield self.profile_ps.create_profile_workexp(record, profile_id, mode='p')
        yield self.candidate_ps.add_candidate_remard(
            user_id=self.current_user.sysuser.id,
            company=form.company,
            position=form.position,
            name=form.name,
            hr_id=position_info.publisher
            )

        self.send_json_success()
