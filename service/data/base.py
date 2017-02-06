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

import glob
import importlib
import re

from app import logger
import conf.common as constant
import conf.help as help_constant
import conf.platform as plat_constant
import conf.qx as qx_constant
import conf.path as path
from setting import settings
from util.common.singleton import Singleton


class DataService:

    __metaclass__ = Singleton

    def __init__(self):
        self.logger = logger
        self.constant = constant
        self.plat_constant = plat_constant
        self.qx_constant = qx_constant
        self.help_constant = help_constant
        self.path = path

        for module in self._search_path():
            p = module.split("/")[-2]
            m = module.split("/")[-1].split(".")[0]
            m_list = [item.title() for item in re.split("_", m)]
            pm_dao = "".join(m_list) + "Dao"
            pm_obj = m + "_dao"
            klass = getattr(
                importlib.import_module('dao.{0}.{1}'.format(p, m)), pm_dao)
            instance = klass()

            setattr(self, pm_obj, instance)

    @staticmethod
    def _valid_conds(conds):
        ret = False
        if not conds:
            return ret
        return isinstance(conds, dict) or isinstance(conds, str)

    @staticmethod
    def _search_path():
        d = settings['root_path'] + "dao/**/*.py"
        return filter(lambda x: not x.endswith("init__.py"), glob.glob(d))
