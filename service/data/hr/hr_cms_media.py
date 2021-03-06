# -*- coding=utf-8 -*-
# Copyright 2017 MoSeeker

"""
:author 陈迪（chendi@moseeker.com）
:date 2017.03.26
"""

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class HrCmsMediaDataService(DataService):

    # @cache(ttl=300)
    # @gen.coroutine
    # def get_medium(self, conds, fields=[]):
    #
    #     if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
    #         self.logger.warn("Warning:[get_medium][invalid parameters], \
    #                 Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
    #         raise gen.Return(ObjectDict())
    #
    #     if not fields:
    #         fields = list(self.hr_media_dao.fields_map.keys())
    #
    #     response = yield self.hr_media_dao.get_record_by_conds(conds, fields)
    #     raise gen.Return(response)

    # @cache(ttl=300)
    @gen.coroutine
    def get_media_list(self, conds, fields=[]):

        if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
            self.logger.warn("Warning:[get_media_list][invalid parameters], \
                    Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.hr_cms_media_dao.fields_map.keys())

        response = yield self.hr_cms_media_dao.get_list_by_conds(conds, fields)
        raise gen.Return(response)

    # @gen.coroutine
    # def get_media_by_ids(self, id_list, list_flag=False):
    #     """
    #     获取指定media_id列表内所有media对象
    #     :param self:
    #     :param id_list:
    #     :param list_flag: 为真返回media列表
    #     :return: {object_hr_media.id: object_hr_media, ...} or [object_hr_media ...]
    #     """
    #     if not id_list:
    #         media_list = []
    #     else:
    #         media_list = yield self.get_media_list(
    #             conds='id in {}'.format(tuple(id_list)).replace(',)', ')'))
    #
    #     media_dict = {m.id: m for m in media_list}
    #     if list_flag:
    #         raise gen.Return([media_dict.get(mid) for mid
    #                           in id_list if media_dict.get(mid)])
    #     raise gen.Return(media_dict)
