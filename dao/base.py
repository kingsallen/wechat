# coding=utf-8

# Copyright 2016 MoSeeker

"""
说明:
Model基类，封装对数据库的访问，对传入参数的处理
"""

from tornado import gen
from tornado.util import ObjectDict

import conf.common as constant
import conf.platform as plat_constant
import conf.qx as qx_constant
from utils.common.db import DB
from utils.common.singleton import Singleton
from utils.tool.date_tool import curr_now


class BaseDao(DB):

    __metaclass__ = Singleton

    def __init__(self):

        """
        :return:
        """

        super(BaseDao,self).__init__()
        self.fields_map = {}
        self.table = ''
        self.constant = constant
        self.plat_constant = plat_constant
        self.qx_constant = qx_constant

    @gen.coroutine
    def query(self, sql, params):

        """

        使用输入的SQL语句进行查询
        使用连接池的方式执行sql，可返回rows、lastrowid等
        :param sql SQl语句
        :return: cursor游标
        """
        self.logger.warn("[warning][{0}][start][time: {1}][sql: {2}]".format(self.__class__.__module__, curr_now(), sql))
        cursor = yield self.pool.execute(sql, params)
        raise gen.Return(cursor)


    @gen.coroutine
    def get_list_by_conds(self, conds, fields, options=[], appends=[], index='', conds_params=[]):

        """
        Select查询，根据限制条件获取结果数组
        :param conds: 限制条件，数组或字符串形式，示例:
        dict{
            'field': value,
            'field': [value, '=|>|<'],
            'field': [value, '<', value, '>'],
        }
        或者"field in (1, 2)"
        :param fields: 需要查询的字段名数组，需要与mysql字段对应
        :param options: SQL前置选项，示例:
        [
            'DISTINCT',
            'SQL_NO_CACHE'
        ]
        :param appends: SQL后置选项，示例:
        [
            'ORDER BY b.id',
            'LIMIT 5'
        ]
        :param index: 支持mysql的USE/IGNORE/FORCE Index的语法，指定索引名称，示例：
        "USE INDEX (index1, index2)"
        :param conds_params: 字符串形式的conds对应的params值，防SQL注入
        :return: 返回查询结果列表数组
        """

        conds, params = self.getConds(conds, conds_params)
        if not conds:
            self.logger.error("Error:[get_list_by_conds][conds error], conds:{0}".format(conds))
            raise gen.Return(list())
        sql = self.select(self.table, conds, fields, options, appends, index)
        cursor = yield self.query(sql, params)
        response = cursor.fetchall()
        if not isinstance(response, list):
            response = list()
        raise gen.Return(response)

    @gen.coroutine
    def get_record_by_conds(self, conds, fields, options=[], appends=[], index=''):

        """
        Select单条查询，根据限制条件获得结果的单条记录
        :param conds: 限制条件，数组或字符串形式，示例见@link get_list_by_conds()
        :param fields: 需要查询的字段名数组，需要与mysql字段对应
        :param options: SQL前置选项
        :param appends: SQL后置选项
        :param index: 强制索引时，指定的索引名称
        :return: 返回查询的结果单条记录
        """

        conds, params = self.getConds(conds)
        if not conds:
            self.logger.error("Error:[get_record_by_conds][conds error], conds:{0}".format(conds))
            raise gen.Return(ObjectDict())
        sql = self.select(self.table, conds, fields, options, appends, index)
        cursor = yield self.query(sql, params)
        response = cursor.fetchone()
        if not isinstance(response, dict):
            response = ObjectDict()
        raise gen.Return(ObjectDict(response))

    @gen.coroutine
    def insert_record(self, fields, options=[]):

        """
        Insert插入，只支持单行插入
        :param fields: 需要插入的字段dict，示例:
        dict{
            'field': value
        }
        :param options: INSERT插入选项，支持"LOW_PRIORITY","DELAYED", "HIGH_PRIORITY", "IGNORE"
        :return: 返回插入后的自增ID
        """

        fields = self.checkFieldType(fields, self.fields_map)
        if not fields:
            self.logger.error("Error:[insert_record][fields error], fields:{0}".format(fields))
            raise gen.Return(None)
        sql, params = self.insert(self.table, fields, options)
        cursor = yield self.query(sql, params)
        insert_id = cursor.lastrowid
        raise gen.Return(insert_id)

    @gen.coroutine
    def update_by_conds(self, conds, fields, options=[], appends=[]):

        """
        Update更新，根据限制条件更新对应的数据库记录
        :param conds: 限制条件，数组或字符串形式，示例见@link get_list_by_conds()
        :param fields: 需要更新的字段键值对，dict形式
        :param options: SQL前置选项
        :param appends: SQL后置条件
        :return:
        """

        fields = self.checkFieldType(fields, self.fields_map)
        if not fields:
            self.logger.error("Error:[update_by_conds][fields error], fields:{0}".format(fields))
            raise gen.Return(False)
        conds, conds_params = self.getConds(conds)
        if not conds:
            self.logger.error("Error:[update_by_conds][conds error], conds:{0}".format(conds))
            raise gen.Return(False)
        sql, params = self.update(self.table, conds, fields, options, appends)
        params_update = []
        params_update.extend(params)
        params_update.extend(list(conds_params))
        cursor = yield self.query(sql, params_update)
        cursor.fetchone()
        rows_count = cursor.rowcount
        if rows_count:
            raise gen.Return(True)
        else:
            raise gen.Return(False)

    @gen.coroutine
    def delete_by_conds(self, conds):

        """
        Delete删除，根据限制条件删除对应的数据库记录
        :param conds: 限制条件，数组或字符串形式，示例见@link get_list_by_conds()
        :return:
        """

        conds, params = self.getConds(conds)
        if not conds:
            self.logger.error("Error:[delete_by_conds][conds error], conds:{0}".format(conds))
            raise gen.Return(None)
        sql = self.delete(self.table, conds)
        cursor = yield self.query(sql, params)
        response = cursor.fetchone()
        raise gen.Return(response)

    @gen.coroutine
    def get_cnt_by_conds(self, conds, fields, appends=[], index=''):

        """
        Select查询记录数
        :param conds: 限制条件，数组或字符串形式，示例见@link get_list_by_conds()
        :param fields: 查询字段
        :param appends: SQL后置选项
        :param index: 支持mysql的USE/IGNORE/FORCE Index的语法，指定索引名称
        :return:
        """

        conds, params = self.getConds(conds)
        if not conds:
            self.logger.error("Error:[get_cnt_by_conds][conds error], conds:{0}".format(conds))
            raise gen.Return(None)
        sql = self.select_cnt(self.table, conds, fields, appends, index)
        cursor = yield self.query(sql, params)
        response = cursor.fetchone()
        raise gen.Return(response)

    @gen.coroutine
    def start_transaction(self):

        """
        开始一个事务，待完善
        :return:
        """

        transaction = self.pool.begin()
        raise gen.Return(transaction)
