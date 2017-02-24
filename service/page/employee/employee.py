# coding=utf-8

from tornado import gen
from service.page.base import PageService

class EmployeePageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_employee_rewards(self, employee_id, company_id):

        ret = yield self.thrift_employee_ds.get_employee_rewards(employee_id, company_id)
        raise gen.Return(ret)

    @gen.coroutine
    def unbind(self, employee_id, company_id, user_id):

        ret = yield self.thrift_employee_ds.unbind(employee_id, company_id, user_id)
        raise gen.Return(ret)

    @gen.coroutine
    def bind(self, binding_params):

        ret = yield self.thrift_employee_ds.bind(binding_params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_recommend_records(self, user_id, type, page_no, page_size):
        """
        推荐历史记录
        :param user_id:
        :param type: 数据类型 1表示浏览人数，2表示浏览人数中感兴趣的人数，3表示浏览人数中投递的人数
        :param page_no:
        :param page_size:
        :return:
        """
        ret = yield self.thrift_useraccounts_ds.get_recommend_records(user_id, type, page_no, page_size)
        raise gen.Return(ret)
