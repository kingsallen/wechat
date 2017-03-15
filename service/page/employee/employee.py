# coding=utf-8

from tornado import gen

from service.page.base import PageService
import conf.common as const
from util.common import ObjectDict
from util.tool.url_tool import make_static_url


class EmployeePageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_employee_rewards(self, employee_id, company_id):

        ret = yield self.thrift_employee_ds.get_employee_rewards(employee_id, company_id)
        return ret
    @gen.coroutine
    def unbind(self, employee_id, company_id, user_id):

        ret = yield self.thrift_employee_ds.unbind(employee_id, company_id, user_id)
        raise gen.Return(ret)

    @gen.coroutine
    def bind(self, binding_params):

        ret = yield self.thrift_employee_ds.bind(binding_params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_recommend_records(self, user_id, req_type, page_no, page_size):
        """
        推荐历史记录
        :param user_id:
        :param type: 数据类型 1表示浏览人数，2表示浏览人数中感兴趣的人数，3表示浏览人数中投递的人数
        :param page_no:
        :param page_size:
        :return:
        """
        ret = yield self.thrift_useraccounts_ds.get_recommend_records(int(user_id), int(req_type), int(page_no), int(page_size))

        score = ObjectDict()
        if ret.score:
            score = ObjectDict({
                "link_viewed_count": ret.score.link_viewed_count,
                "interested_count": ret.score.interested_count,
                "applied_count": ret.score.applied_count
            })
        recommends = list()
        if ret.recommends:
            for e in ret.recommends:
                recom = ObjectDict({
                    "status": e.status,
                    "headimgurl": make_static_url(e.headimgurl or const.SYSUSER_HEADIMG),
                    "is_interested": e.is_interested,
                    "applier_name": e.applier_name,
                    "applier_rel": e.applier_rel,
                    "view_number": e.view_number,
                    "position": e.position,
                    "click_time": e.click_time,
                    "recom_status": e.recom_status
                })
                recommends.append(recom)

        res = ObjectDict({
            "has_recommends": ret.hasRecommends if ret.hasRecommends else False,
            "score": score,
            "recommends": recommends
        })

        raise gen.Return(res)
