# -*- coding: utf-8 -*-

'''

说明:
DB公共处理类
'''
import ujson

from tornado_mysql import pools, cursors

from setting import settings
from utils.common.log import Logger
from utils.tool.date_tool import is_time_valid
import conf.common as constant


class DB(object):

    def __init__(self):
        self.pool = pools.Pool(
            dict(host=settings['mysql_host'],
                 port=settings['mysql_port'],
                 user=settings['mysql_user'],
                 passwd=settings['mysql_password'],
                 db=settings['mysql_database'],
                 cursorclass=cursors.DictCursor,
                 charset='utf8mb4'),
            max_idle_connections=1,
            max_recycle_sec=3
        )
        self.logger = Logger()

    def getConds(self, conds, conds_params=[]):

        '''
        对传入的SQL限制条件数组或字符串，转换成MYSQL可识别的形式
        :param conds: 字符串或者数组格式的SQL限制条件, 格式示例：
        dict{
            'field': value,
            'field': [value, '=|>|<'],
            'field': [value, '<', value, '>'],
        }
        或者"field in (1, 2)"
        :param conds_params: 字符串形式的conds对应的params值，防SQL注入
        :return: 返回转化后的SQL限制条件（数组）和params值 可以防止SQL注入，不符合条件的返回None
        '''

        if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
            self.logger.error("Error:[getConds][conds type error], conds:{0}, type:{1}".format(conds, type(conds)))
            return False, ()

        conds_res = []
        params = []
        if isinstance(conds, str):
            conds_res.append(conds)
            params.extend(conds_params)
        else:
            for key, value in conds.items():
                if isinstance(value, list):
                    if len(value) == 2:
                        frag = "{0} {1} %s".format(key, value[1])
                        conds_res.append(frag)
                        params.append(value[0])
                    elif len(value) == 4:
                        frag_fir = "{0} {1} %s".format(key, value[1])
                        frag_sec = "{0} {1} %s".format(key, value[3])
                        conds_res.append(frag_fir)
                        conds_res.append(frag_sec)
                        params.append(value[0])
                        params.append(value[2])
                    else:
                        self.logger.error("Error:[getConds][value length error], value:{0}, "
                                       "length:{1}".format(value, len(value)))
                        return False, ()
                elif isinstance(value, str) or isinstance(value, int):
                    frag = "{0} = %s".format(key)
                    conds_res.append(frag)
                    params.append(value)
                else:
                    self.logger.error("Error:[getConds][value type error][only accept list/int/str], key: {0}, value:{1}, "
                                "type:{2}".format(key, value, type(value)))
                    return False, ()

        return conds_res, params

    def checkFieldType(self, fields={}, maps={}):

        '''
        对插入或者更新的字段进行类型检查和转换，类型映射中没有的默认为字符串
        :param fields: 待插入或者更新的字段数组
        :param maps: dao中定义的返回结果类型映射表
        :return: 成功返回类型转换后的数组，未转换或输入错误做str处理
        '''

        if fields is None or not isinstance(fields, dict):
            self.logger.error("Error:[checkFieldType][fields type error], fields:{0}, type:{1}".format(fields, type(fields)))
            return False

        if maps is None or not isinstance(maps, dict):
            self.logger.error("Error:[checkFieldType][types type error], types:{0}, type:{1}".format(maps, type(maps)))
            return False

        for key, value in maps.items():
            if fields.get(key, 0):
                if value == constant.TYPE_INT:
                    if not isinstance(fields[key], int):
                        self.logger.error("Error:[checkFieldType][field type error], Detail:[key:{0} value:{0} "
                                    "should by int]".format(key, fields[key]))
                        return False
                    fields[key] = int(fields[key])
                elif value == constant.TYPE_JSON:
                    if isinstance(fields[key], list):
                        fields[key] = ujson.encode(fields[key])
                    elif not isinstance(fields[key], str):
                        self.logger.error("Error:[checkFieldType][field type error], Detail:[key:{0} value:{0} "
                                    "should by json]".format(key, fields[key]))
                        return False
                elif value == constant.TYPE_FLOAT:
                    if not isinstance(fields[key], float):
                        self.logger.error("Error:[checkFieldType][field type error], Detail:[key:{0} value:{0} "
                                    "should by float]".format(key, fields[key]))
                        return False
                    fields[key] = float(fields[key])
                elif value == constant.TYPE_TIMESTAMP:
                    if not is_time_valid(fields[key], constant.TIME_FORMAT):
                        self.logger.error("Error:[checkFieldType][field type error], Detail:[key: {0} value:{1} format "
                                    "should by {2}]".format(key, fields[key], constant.TIME_FORMAT))
                        return False
                else:
                    fields[key] = str(fields[key])

        return fields

    def select(self, table, conds=[], fields=[], options=[], appends=[], index=''):

        '''
        Select查询
        :param table: 表名
        :param conds: 限制条件
        :param fields: 查询字段
        :param options: SQL前置条件
        :param appends: SQL后置选项
        :param index: 支持mysql的USE/IGNORE/FORCE Index的语法，指定索引名称
        :return: 返回拼装SQL, params 可以防止SQL注入
        '''

        sql = "SELECT "
        # SQL前置条件
        if isinstance(options, list) and len(options) > 0:
            sql += " ".join(options)
        # 查询字段
        if isinstance(fields, list) and len(fields) > 0:
            sql += ", ".join(fields)
        else:
            self.logger.error("Error:[select][fields error], fields:{0}, type:{1}, "
                           "length{2}".format(fields, type(fields), len(fields)))
            return False

        sql += " FROM {0}".format(table)
        # 限制条件
        if isinstance(conds, list) and len(conds) > 0:
            sql += " WHERE "
            sql += " AND ".join(conds)

        # SQL后置选项
        if isinstance(appends, list) and len(appends) > 0:
            sql += " ".join(appends)

        if index:
            sql += index

        return sql

    def insert(self, table, fields, options=[]):

        '''
        Insert插入
        :param table: 数据表
        :param fields: 需要插入的字段dict
        :param options: INSERT插入选项，支持"LOW_PRIORITY","DELAYED", "HIGH_PRIORITY", "IGNORE"
        :return: 返回拼装SQL, params值
        '''

        sql = "INSERT "
        # SQL前置条件
        if isinstance(options, list) and len(options) > 0:
            sql += ' '.join(options)
        sql += " INTO {0}(".format(table)

        if isinstance(fields, dict):
            sql += ", ".join(fields.keys())
        sql += ") VALUES ("

        if isinstance(fields, dict):
            for item in fields.values():
                sql += "%s, "
        sql = sql[:-2]
        sql += ")"

        return sql, fields.values()

    def update(self, table, conds, fields, options=[], appends=[]):

        '''
        Update更新，根据限制条件更新对应的数据库记录
        :param table: 数据表
        :param conds: 限制条件，数据或者字符串形式即可
        :param fields: 需要更新的字段名dict
        :param options: SQL前置选项
        :param appends: SQL后置条件
        :return: 拼装的SQL
        '''

        sql = "UPDATE "
        # SQL前置条件
        if isinstance(options, list) and len(options) > 0:
            sql += " ".join(options)
        sql += " {0} SET ".format(table)

        # 更新字段
        params = []
        if isinstance(fields, dict):
            for key, value in fields.items():
                sql += "{0} = %s, ".format(key)
                params.append(value)
        else:
            self.logger.error("Error:[update][fields error], fields:{0}, type:{1}".format(fields, type(fields)))
            return False

        sql = sql[:-2]
        # 限制条件
        if isinstance(conds, list) and len(conds) > 0:
            sql += " WHERE "
            sql += " and ".join(conds)
        # SQL后置选项
        if isinstance(appends, list) and len(appends) > 0:
            sql += " ".join(appends)

        return sql, params

    def delete(self, table, conds):

        '''
        Delete删除，根据限制条件删除对应的数据库记录
        :param table: 数据表
        :param conds: 限制条件，数据或者字符串形式即可
        :return: 拼装的SQL
        '''

        sql = "DELETE FROM {0}".format(table)

        # 限制条件
        if isinstance(conds, list) and len(conds) > 0:
            sql += " WHERE "
            sql += " and ".join(conds)

        return sql

    def select_cnt(self, table, conds=[], fields=[], appends=[], index=''):

        '''
        Select查询记录数
        :param table: 表名
        :param conds: 限制条件
        :param fields: 查询字段
        :param options: SQL前置条件
        :param appends: SQL后置选项
        :param index: 支持mysql的USE/IGNORE/FORCE Index的语法，指定索引名称
        :return: 返回拼装SQL
        '''

        sql = "SELECT "
        # 查询字段
        if isinstance(fields, list) and len(fields) > 0:
            sql_tmp = ''
            for field in fields:
                sql_tmp += "COUNT({}), ".format(field)
            sql += sql_tmp
        else:
            self.logger.error("Error:[select_cnt][fields error], fields:{0}, type:{1}, "
                           "length{2}".format(fields, type(fields), len(fields)))
            return False

        sql += " FROM {0}".format(table)
        # 限制条件
        if isinstance(conds, list) and len(conds) > 0:
            sql += " WHERE "
            sql += " and ".join(conds)
        # SQL后置选项
        if isinstance(appends, list) and len(appends) > 0:
            sql += " ".join(appends)

        if index:
            sql += index

        return sql