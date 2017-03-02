# coding=utf-8

# @Time    : 1/22/17 11:06
# @Author  : panda (panyuxin@moseeker.com)
# @File    : usercenter.py
# @DES     :

# Copyright 2016 MoSeeker

from tornado import gen

from service.page.base import PageService
from util.common import ObjectDict
from util.tool.str_tool import gen_salary
from util.tool.date_tool import jd_update_date, str_2_date

from thrift_gen.gen.useraccounts.service.UserCenterService import Client as UserCenterServiceClient
from service.data.infra.framework.client.client import ServiceClientFactory
from service.data.infra.framework.common.config import CONF

class UsercenterPageService(PageService):

    usercenter_service_cilent = ServiceClientFactory.get_service(
        UserCenterServiceClient, CONF)

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_user(self, user_id):
        """获得用户数据"""

        ret = yield self.infra_user_ds.get_user(user_id)
        raise gen.Return(ret)

    @gen.coroutine
    def update_user(self, user_id, params):
        """更新用户数据"""

        ret = yield self.infra_user_ds.put_user(user_id, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_resetpassword(self, mobile, password):
        """重置密码"""

        ret = yield self.infra_user_ds.post_resetpassword(mobile, password)
        raise gen.Return(ret)

    @gen.coroutine
    def post_login(self, params):
        """用户登录
        微信 unionid, 或者 mobile+password, 或者mobile+code, 3选1
        :param mobile: 手机号
        :param password: 密码
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
    def post_register(self, mobile, password):
        """用户注册
        :param mobile: 手机号
        :param password: 密码
        """

        ret = yield self.infra_user_ds.post_register(mobile, password)
        raise gen.Return(ret)

    @gen.coroutine
    def post_ismobileregistered(self, mobile):
        """判断手机号是否已经注册
        :param mobile: 手机号
        """

        ret = yield self.infra_user_ds.post_ismobileregistered(mobile)
        raise gen.Return(ret)

    @gen.coroutine
    def get_fav_positions(self, user_id):
        """获得职位收藏"""

        ret = yield self.thrift_useraccounts_ds.get_fav_positions(user_id)
        obj_list = list()
        for e in ret:
            fav_pos = ObjectDict()
            fav_pos['id'] = e.id
            fav_pos['title'] = e.title
            fav_pos['time'] = e.time
            fav_pos['department'] = e.department
            fav_pos['city'] = e.city
            fav_pos['salary'] = gen_salary(str(e.salary_top), str(e.salary_bottom))
            fav_pos['update_time'] = jd_update_date(str_2_date(e.update_time, self.constant.TIME_FORMAT))
            fav_pos['states'] = "已过期" if e.status == 2 else ""
            obj_list.append(fav_pos)
        raise gen.Return(obj_list)

    @gen.coroutine
    def get_applied_applications(self, user_id):
        """获得求职记录"""

        ret = yield self.thrift_useraccounts_ds.get_applied_applications(user_id)
        obj_list = list()
        for e in ret:
            app_rec = ObjectDict()
            app_rec['id'] = e.id
            app_rec['position_title'] = e.title
            app_rec['company_name'] = e.department
            app_rec['status_name'] = e.status
            app_rec['time'] = e.time
            obj_list.append(app_rec)
        raise gen.Return(obj_list)

    @gen.coroutine
    def get_applied_progress(self, app_id, user_id):
        """
        求职记录中的求职详情进度
        :param app_id:
        :param user_id:
        :return:
        """
        ret = yield self.thrift_useraccounts_ds.get_applied_progress(app_id, user_id)

        time_lines = list()
        if ret.status_timeline:
            for e in ret.status_timeline:
                timeline = ObjectDict({
                    "date": e.date,
                    "event": e.event,
                    "hide": e.hide,
                    "step_status": e.step_status,
                })
                time_lines.append(timeline)

        res = ObjectDict({
            "pid": e.pid,
            "position_title": e.position_title,
            "company_name": e.company_name,
            "step": e.step,
            "step_status": e.step_status,
            "status_timeline": time_lines,
        })

        raise gen.Return(res)
