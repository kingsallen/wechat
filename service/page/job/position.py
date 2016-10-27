# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.page.base import PageService
import conf.common as const
import conf.path as path
from util.common import ObjectDict
from util.tool.http_tool import http_get
from util.tool.url_tool import make_url
from util.tool.date_tool import jd_update_date
from util.tool.str_tool import gen_salary, split


class PositionPageService(PageService):

    def __init__(self, logger):
        super().__init__(logger)

    @gen.coroutine
    def get_position(self, position_id, fields=None):

        fields = fields or []
        position = ObjectDict()
        conds = {'id': position_id}
        position_res = yield self.job_position_ds.get_position(conds, fields)
        position_ext_res = yield self.job_position_ext_ds.get_position_ext(conds, fields)
        if not position_res:
            raise gen.Return(position)

        # 前置处理
        # 更新时间
        update_time = jd_update_date(position_res.update_time)
        # 月薪
        salary = gen_salary(position_res.salary_top, position_res.salary_bottom)

        # 职位基础信息拼装
        position = ObjectDict({
            'id': position_res.id,
            'title': position_res.title,
            'company_id': position_res.company_id,
            'department': position_res.department,
            'candidate_source': self.constant.CANDIDATE_SOURCE.get(str(position_res.candidate_source)),
            'employment_type': self.constant.EMPLOYMENT_TYPE.get(str(position_res.employment_type)),
            'update_time': update_time,
            "salary": salary,
            "city": position_res.city,
            "occupation": position_res.occupation,
            "experience": position_res.experience
                          + (self.constant.EXPERIENCE_UNIT if position_res.experience else '')
                          + (self.constant.POSITION_ABOVE if position_res.experience_above else ''),
            "language": position_res.language,
            "count": position_res.count,
            "degree": self.constant.DEGREE.get(str(position_res.degree))
                      + self.constant.POSITION_ABOVE if position_res.degree_above else '',
            "management": position_res.management,
            "accountabilities": position_res.accountabilities,
            "requirement": position_res.requirement,
            "feature": position_res.feature,
            "status": position_res.status == 0,
            "publisher": position_res.publisher,
            "share_tpl_id": position_res.share_tpl_id,
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

        # 职位自定义字段
        if position_ext_res.job_custom_id:
            job_custom_res = yield self.job_custom_ds.get_custom(conds={"id": position_ext_res.job_custom_id})
            position.job_custom = job_custom_res.name

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

    @gen.coroutine
    def get_real_company_id(self, publisher, company_id):
        """获得职位所属公司id
        1.首先根据 hr_company_account 获得 hr 帐号与公司之间的关系，获得company_id
        2.如果1取不到，则直接取职位中的 company_id"""

        hr_company_account = yield self.hr_company_account_ds.get_company_account(conds={"account_id": publisher})
        real_company_id = hr_company_account.company_id or company_id

        raise gen.Return(real_company_id)

    @gen.coroutine
    def get_recommend_positions(self, position_id):
        """获得 JD 页推荐职位
        reference: https://wiki.moseeker.com/position-api.md#recommended

        :param position_id: 职位 id
        """

        req = ObjectDict({
            'pid': position_id,
        })
        try:
            response = list()
            ret = yield http_get(self.path.POSITION_RECOMMEND, req)
            if ret.status == 0:
                response = ret.data
        except Exception as error:
            self.logger.warn(error)

        raise gen.Return(response)

