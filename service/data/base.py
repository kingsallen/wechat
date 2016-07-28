# coding=utf-8

'''
:author 潘煜昕（panyuxin@moseeker.com）
:date 2016.07.26

说明:
dataservice的父类
负责与DAO交互，实现原子性的操作。一个DAO对应一个dataservice，不能被handler调用，只能被pageservice调用，可被多个pageservice调用
dataservice之间不能相互调用
可以根据表名创建dataservice
'''

import importlib

from utils.common.log import Logger
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

class DataService:

    __metaclass__ = Singleton

    def __init__(self):

        self.logger = Logger
        self.constant = constant
        self.plat_constant = plat_constant
        self.qx_constant = qx_constant

        self.base_dao = getattr(importlib.import_module('dao.{0}'.format('base')),
                                'BaseDao')()

        self.hr_company_dao = getattr(importlib.import_module('dao.{0}.{1}'.format('hr', 'hr_company')),
                                      'HrCompanyDao')()
        self.hr_company_conf_dao = getattr(importlib.import_module('dao.{0}.{1}'.format('hr', 'hr_company_conf')),
                                           'HrCompanyConfDao')()
        self.hr_wx_wechat_dao = getattr(importlib.import_module('dao.{0}.{1}'.format('hr', 'hr_wx_wechat')),
                                        'HrWxWechatDao')()

        self.job_position_dao = getattr(importlib.import_module('dao.{0}.{1}'.format('job', 'job_position')),
                                        'JobPositionDao')()
        self.job_custom_dao = getattr(importlib.import_module('dao.{0}.{1}'.format('job', 'job_custom')),
                                        'JobCustomDao')()
