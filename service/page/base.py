# coding=utf-8

"""
:author 潘煜昕（panyuxin@moseeker.com）
:date 2016.07.22

说明:
pageservice的父类
负责与handler交互，不能直接与DAO交互。
一个pageservice能调用多个dataservice，pageservice只能被handler调用
pageservice之间可以相互调用，但不建议
可以根据业务类型创建pageservice
"""

import re
import importlib
import glob

from globals import logger
from globals import es, redis, sa
from setting import settings
import conf.common as constant
import conf.platform as plat_constant
import conf.qx as qx_constant
import conf.helper as help_constant
import conf.path as path
from util.common.singleton import Singleton


class PageService:
    __metaclass__ = Singleton

    def __init__(self):

        """
        初始化dataservice
        :return:
        """
        self.logger = logger
        self.redis = redis
        self.es = es
        self.sa = sa
        self.settings = settings
        self.constant = constant
        self.plat_constant = plat_constant
        self.qx_constant = qx_constant
        self.path = path
        self.help_constant = help_constant

        d = settings['root_path'] + "/service/data/**/*.py"
        for module in filter(lambda x: not x.endswith("init__.py"), glob.glob(d)):
            p = module.split("/")[-2]
            m = module.split("/")[-1].split(".")[0]
            m_list = [item.title() for item in re.split("_", m)]
            pm_ds = "".join(m_list) + "DataService"
            pm_obj = m + "_ds"

            klass = getattr(
                importlib.import_module('service.data.{0}.{1}'.format(p, m)),
                pm_ds)
            instance = klass()

            setattr(self, pm_obj, instance)
