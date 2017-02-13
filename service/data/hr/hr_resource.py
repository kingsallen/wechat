# coding=utf-8
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.12.20

"""

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class HrResourceDataService(DataService):

    @cache(ttl=300)
    @gen.coroutine
    def get_resource(self, conds, fields=[]):

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warn("Warning:[get_resource][invalid parameters], \
                    Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_resource_dao.fields_map.keys())

        response = yield self.hr_resource_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @cache(ttl=300)
    @gen.coroutine
    def get_resource_list(self, conds, fields=[]):

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warn("Warning:[get_resource_list][invalid parameters], \
                    Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.hr_resource_dao.fields_map.keys())

        response = yield self.hr_resource_dao.get_list_by_conds(conds, fields)
        raise gen.Return(response)

    @gen.coroutine
    def get_resource_by_ids(self, id_list, list_flag=False):
        """
        获取指定resource_id列表内所有resource对象
        :param self:
        :param id_list:
        :param list_flag: 为真返回resource列表
        :return: {hr_resource.id: hr_resource, ...} or [hr_resource ...]
        """
        if not id_list:
            resource_list = []
        else:
            resource_list = yield self.get_resource_list(
                conds='id in {}'.format(tuple(id_list)).replace(',)', ')'),
                fields=['id', 'res_url', 'res_type']
            )

        resource_dict = {r.id: r for r in resource_list}
        if list_flag:
            raise gen.Return([resource_dict.get(rid) for rid
                              in id_list if resource_dict.get(rid)])
        raise gen.Return(resource_dict)
