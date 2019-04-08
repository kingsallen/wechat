# coding=utf-8


from tornado import gen

from service.page.base import PageService
from util.common import ObjectDict
from util.tool.str_tool import gen_salary, set_literl
from util.tool.date_tool import jd_update_date, str_2_date
import conf.common as const
from util.common.decorator import log_coro


class UsercenterPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_user(self, user_id):
        """获得用户数据"""

        ret = yield self.infra_user_ds.get_user_by_user_id(user_id)
        raise gen.Return(ret)

    @gen.coroutine
    def get_my_info(self, user_id, company_id):
        """获得用户数据"""
        params = ObjectDict({
            "company_id": company_id
        })
        ret = yield self.infra_user_ds.get_my_info(user_id, params)
        raise gen.Return(ret)

    @gen.coroutine
    def update_user(self, user_id, params):
        """更新用户数据"""
        params.update(id=user_id)

        ret = yield self.infra_user_ds.put_user(params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_resetpassword(self, country_code, mobile, password):
        """重置密码"""

        ret = yield self.infra_user_ds.post_resetpassword(country_code, mobile, password)
        raise gen.Return(ret)

    @gen.coroutine
    def post_login(self, params):
        """用户登录
        微信 unionid, 或者 mobile+password, 或者mobile+code, 3选1
        :param mobile: 手机号
        :param password: 密码，非加密的原密码
        :param code: 手机验证码
        :param unionid: 微信 unionid
        """

        ret = yield self.infra_user_ds.post_login(params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_logout(self, user_id):
        """用户登出
        :param user_id:
        """

        ret = yield self.infra_user_ds.post_logout(user_id)
        raise gen.Return(ret)

    @gen.coroutine
    def post_register(self, user_creation_form):
        """用户注册"""

        params = ObjectDict({
                "user": {
                    'username':    user_creation_form.username,
                    'mobile':      user_creation_form.mobile,
                    'password':    user_creation_form.password,
                    'register_ip': user_creation_form.register_ip,
                    'countryCode': user_creation_form.country_code,
                    'register_time': user_creation_form.register_time
                }
            })

        ret = yield self.infra_user_ds.post_register(params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_ismobileregistered(self, mobile, country_code=86):
        """判断手机号是否已经注册
        :param country_code
        :param mobile: 手机号
        """

        ret = yield self.infra_user_ds.post_ismobileregistered(mobile, country_code)
        raise gen.Return(ret)

    @gen.coroutine
    def get_collect_positions(self, user_id):
        """获得职位收藏"""
        params = {
            "user_id": user_id
        }
        ret = yield self.infra_user_ds.infra_get_collect_positions(params)
        obj_list = list()
        for e in ret.data:
            fav_pos = ObjectDict()
            fav_pos['id'] = e.id
            fav_pos['title'] = e.title
            fav_pos['time'] = e.time
            fav_pos['department'] = e.department
            fav_pos['city'] = e.city
            fav_pos['salary'] = gen_salary(e.salary_top, e.salary_bottom)
            fav_pos['update_time'] = jd_update_date(str_2_date(e.update_time, self.constant.TIME_FORMAT))
            fav_pos['states'] = "已过期" if e.status in [const.POSITION_STATUS_DELETED, const.POSITION_STATUS_WITHDRAWN] else ""
            fav_pos['signature'] = e.signature
            obj_list.append(fav_pos)
        raise gen.Return(obj_list)

    @log_coro(threshold=20)
    @gen.coroutine
    def get_user_position_stared_list(self, user_id, position_id_list):
        """返回用户感兴趣职位列表"""
        fav_position_id_list = []
        if user_id is None or position_id_list is None:
            return fav_position_id_list
        params = {"user_id": user_id,
                  "position_ids": position_id_list}
        ret = yield self.infra_user_ds.infra_get_fav_positions(params)
        fav_position_list = ret.data
        if fav_position_list:
            fav_position_id_list = [e.position_id for e in fav_position_list]
        return fav_position_id_list

    @log_coro(threshold=20)
    @gen.coroutine
    def get_applied_applications_list(self, user_id, position_id_list):
        """返回用户求职记录列表"""
        applied_applications_id_list = []
        if user_id is None or position_id_list is None:
            return applied_applications_id_list
        param = dict(conds={'applier_id': user_id},
                     fields=['position_id'])
        if position_id_list and isinstance(position_id_list, list):
            param.update(appends=["and position_id in %s" % set_literl(position_id_list)])
        applied_applications_list = yield self.job_application_ds.get_applied_applications_list(**param)
        if applied_applications_list:
            applied_applications_id_list = [e.position_id for e in applied_applications_list]
        return applied_applications_id_list

    @gen.coroutine
    def get_applied_applications(self, user_id, company_id, page_no, page_size):
        """获得求职记录列表"""

        res = yield self.infra_user_ds.get_applied_applications(user_id, company_id, page_no, page_size)
        if res.code != const.NEWINFRA_API_SUCCESS:
            ret = []
        else:
            ret = res.data
        obj_list = list()
        for e in ret.data:
            e = ObjectDict(e)
            app_rec = ObjectDict()
            app_rec['id'] = e.id
            app_rec['position_title'] = e.position_title
            app_rec['company_name'] = e.company_name
            app_rec['phase'] = e.phase
            app_rec['time'] = e.time
            app_rec['signature'] = e.signature
            app_rec['pstatus'] = e.status
            obj_list.append(app_rec)
        raise gen.Return(obj_list)

    @gen.coroutine
    def get_applied_progress(self, user_id, app_id):
        """
        求职记录中的求职详情进度
        :param app_id:
        :param user_id:
        :return:
        """
        res = yield self.infra_user_ds.get_applied_progress(user_id, app_id)
        if res.code != const.NEWINFRA_API_SUCCESS:
            ret = []
        else:
            ret = res.data

        time_lines = list()
        if ret.operations:
            for e in ret.operations:
                timeline = ObjectDict({
                    "date": e["date"],
                    "description": e["description"],
                    "display": e["display"],
                    "id": e["id"],
                    "status": e["pass"],
                })
                time_lines.append(timeline)

        phases = list()
        if ret.phases:
            current_phase_id = [item for item in ret.phases if int(item['pass']) != 3][-1]['id'] #pass不是"无状态(pass不等于3)"[无状态表示还没到当前phase]的所有phases的排在list最后的一个phase为当前状态
            for e in ret.phases:
                if e["id"] == current_phase_id:
                    phase = ObjectDict({
                        "id": e["id"],
                        "name": e["name"],
                        "status": e["pass"],  # e.pass会报错
                        "is_current": 1
                    })
                else:
                    phase = ObjectDict({
                        "id": e["id"],
                        "name": e["name"],
                        "status": e["pass"], #e.pass会报错
                        "is_current": 0
                    })
                phases.append(phase)

        res = ObjectDict({
            "pid": ret.position_id,
            "position_title": ret.title,
            "company_name": ret.company_name,
            "phases": phases,
            "status_timeline": time_lines,
        })

        raise gen.Return(res)
