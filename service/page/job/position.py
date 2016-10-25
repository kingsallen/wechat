# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.page.base import PageService
from util.tool.date_tool import jd_update_date
from util.tool.str_tool import gen_salary, split
import conf.common as const
from util.common import ObjectDict


class PositionPageService(PageService):

    def __init__(self, logger):
        super().__init__(logger)

    @gen.coroutine
    def get_position(self, conds, fields=None):

        fields = fields or []

        position = ObjectDict()

        position_res = yield self.job_position_ds.get_position(conds, fields)
        if not position_res:
            raise gen.Return(position)

        update_time = jd_update_date(position_res.get('update_time', ''))

        # 前置处理
        # 月薪
        salary = gen_salary(
            position_res.get("salary_top"), position_res.get("salary_bottom"))

        # 职位基础信息拼装
        position = ObjectDict({
            'id': position_res.get('id', ''),
            'title': position_res.get('title', ''),
            'company_id': int(position_res.get('company_id', 0)),
            'department': position_res.get('department', ''),
            'candidate_source': self.constant.CANDIDATE_SOURCE.get(str(position_res.get('candidate_source', 0))),
            'employment_type': self.constant.EMPLOYMENT_TYPE.get(str(position_res.get('employment_type', 0))),
            'update_time': update_time,
            "salary": salary,
            "city": position_res.get('city', ''),
            "occupation": position_res.get('occupation', ''),
            "experience": position_res.get('experience', '')
                          + (self.constant.EXPERIENCE_UNIT if position_res.get('experience', '') else '')
                          + (self.constant.POSITION_ABOVE if position_res.get('experience_above', 0) else ''),
            "language": position_res.get('language', ''),
            "count": int(position_res.get('count', 0)),
            "degree": self.constant.DEGREE.get(str(position_res.get('degree', 0)))
                      + self.constant.POSITION_ABOVE if position_res.get('degree_above', 0) else '',
            "management": position_res.get('management', ''),
            "accountabilities": position_res.get('accountabilities', ''),
            "requirement": position_res.get('requirement', ''),
            "feature": position_res.get('feature', ''),
            "overdue": False if position_res.get('status', 0) == 0 else True,
            "share_tpl_id": position_res.get('share_tpl_id', 0)
        })

        # 后置处理：
        # 福利特色 需要分割
        if position.feature:
            position_res.feature = split(position.feature, ["#"])

        # 需要折行
        if position.accountabilities:
            position_res.accountabilities = split(position.accountabilities)
        if position.requirement:
            position_res.requirement = split(position.requirement)

        # 自定义分享模板
        if position.share_tpl_id:
            share_conf = yield self.__get_share_conf(position_res.share_tpl_id)
            position.share_title = share_conf.title
            position.share_description = share_conf.share_description

        raise gen.Return(position)

    @gen.coroutine
    def get_positions_list(self, conds, fields, options=[], appends=[]):

        """
        获得职位列表
        :param conds:
        :param fields:
        :param options:
        :param appends:
        :return:
        """

        positions_list = yield self.job_position_ds.get_positions_list(conds, fields, options, appends)
        raise gen.Return(positions_list)

    @gen.coroutine
    def is_position_stared_by(self, position_id, user_id):
        """返回用户是否收藏了职位"""

        fav = yield self.user_fav_position_ds.get_user_fav_position({
            "position_id": position_id,
            "user_id": user_id,
            "favorite": const.FAV_YES
        })
        raise gen.Return(bool(fav))

    @gen.coroutine
    def get_hr_info(self, publisher):
        """获取 hr 信息"""
        hr_account = yield self.user_hr_account_ds.get_hr_account({
            "id": publisher
        })
        hr_wx_user = yield self.user_wx_user_ds.get_wxuser({
            "id": hr_account.wxuser_id
        })
        raise gen.Return((hr_account, hr_wx_user))

    @gen.coroutine
    def __get_share_conf(self, conf_id):
        """获取职位自定义分享模板"""
        ret = yield self.job_position_share_tpl_conf_ds.get_share_conf({
            "id": conf_id
        })
        raise gen.Return(ret)
