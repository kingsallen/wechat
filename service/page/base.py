# coding=utf-8

# Copyright 2016 MoSeeker

"""
:author 潘煜昕（panyuxin@moseeker.com）
:date 2016.07.22

说明:
pageservice的父类
负责与handler交互，不能直接与DAO交互。一个pageservice能调用多个dataservice，pageservice只能被handler调用
pageservice之间可以相互调用，但不建议
可以根据业务类型创建pageservice
"""

import importlib

from utils.common.log import Logger
from settings import settings
import conf.common as constant
import conf.platform as plat_constant
import conf.qx as qx_constant
import conf.help as help_constant

class Singleton(type):

    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kw)
        return cls._instance

class PageService:

    __metaclass__ = Singleton

    def __init__(self):

        """
        初始化dataservice
        :return:
        """
        self.logger = Logger()
        self.settings = settings
        self.constant = constant
        self.plat_constant = plat_constant
        self.qx_constant = qx_constant

        self.hr_company_ds = getattr(importlib.import_module('service.data.{0}.{1}'.format('hr', 'hr_company')),
                                     'HrCompanyDataService')()
        self.hr_company_conf_ds = getattr(importlib.import_module('service.data.{0}.{1}'.format('hr', 'hr_company_conf')),
                                          'HrCompanyConfDataService')()
        self.hr_wx_wechat_ds = getattr(importlib.import_module('service.data.{0}.{1}'.format('hr', 'hr_wx_wechat')),
                                       'HrWxWechatDataService')()
        self.config_sys_theme_ds = getattr(importlib.import_module('service.data.{0}.{1}'.format('config', 'config_sys_theme')),
                                       'ConfigSysThemeDataService')()
        self.job_position_ds = getattr(importlib.import_module('service.data.{0}.{1}'.format('job', 'job_position')),
                                       'JobPositionDataService')()
        self.job_custom_ds = getattr(importlib.import_module('service.data.{0}.{1}'.format('job', 'job_custom')),
                                       'JobCustomDataService')()

