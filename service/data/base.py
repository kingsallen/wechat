# coding=utf-8

# Copyright 2016 MoSeeker

"""
:author 潘煜昕（panyuxin@moseeker.com）
:date 2016.07.26

说明:
dataservice的父类
负责与DAO交互，实现原子性的操作。一个DAO对应一个dataservice，不能被handler调用，只能被pageservice调用，可被多个pageservice调用
dataservice之间不能相互调用
可以根据表名创建dataservice
"""

import re
import glob
import importlib
import conf.common as constant
import conf.platform as plat_constant
import conf.qx as qx_constant
import conf.help as help_constant

from setting import settings
from utils.common.decorator import cache
from app import logger
from utils.common.singleton import Singleton
import pprint

class DataService:

    __metaclass__ = Singleton

    def __init__(self, logger):
        self.logger = logger
        self.constant = constant
        self.plat_constant = plat_constant
        self.qx_constant = qx_constant
        self.help_constant = help_constant

        for module in self.search_path():
            p = module.split("/")[-2]
            m = module.split("/")[-1].split(".")[0]
            m_list = [item.title() for item in re.split("_", m)]
            pm_dao = "".join(m_list) + "Dao"
            pm_obj = m + "_dao"
            klass = getattr(
                importlib.import_module('dao.{0}.{1}'.format(p, m)), pm_dao)
            instance = klass(self.logger)
            setattr(self, pm_obj, instance)

    def _condition_isvalid(self, conds, method_name):
        if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
            self.logger.warn("Warning:[{2}][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds), method_name))
            return False
        return True

    @staticmethod
    def is_invalid_conds(conds=None):
        return (conds is None or
                not (isinstance(conds, dict) or isinstance(conds, str)))

    @staticmethod
    def search_path():
        d = settings['root_path'] + "dao/**/*.py"
        return filter(lambda x: not x.endswith("init__.py"), glob.glob(d))
