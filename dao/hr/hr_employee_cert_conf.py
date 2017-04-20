# coding=utf-8

# @Time    : 10/27/16 12:13
# @Author  : panda (panyuxin@moseeker.com)
# @File    : hr_employee_cert_conf.py
# @DES     : 部门员工配置表

# Copyright 2016 MoSeeker

from dao.base import BaseDao


class HrEmployeeCertConfDao(BaseDao):

    def __init__(self):
        super(HrEmployeeCertConfDao, self).__init__()
        self.table = "hr_employee_cert_conf"
        self.fields_map = {
            "id":                   self.constant.TYPE_INT,
            "company_id":           self.constant.TYPE_INT,
            "is_strict":            self.constant.TYPE_INT,  # 是否严格0：严格，1：不严格
            "email_suffix":         self.constant.TYPE_STRING, # 邮箱后缀
            "create_time":          self.constant.TYPE_TIMESTAMP,
            "update_time":          self.constant.TYPE_TIMESTAMP,
            "disable":              self.constant.TYPE_INT,  # 是否启用 0：启用1：禁用
            "bd_add_group":         self.constant.TYPE_INT,  # 用户绑定时需要加入员工组Flag, 0:需要添加到员工组 1:不需要添加到员工组
            "bd_use_group_id":      self.constant.TYPE_INT,  # 用户绑定时需要加入员工组的分组编号
            "auth_mode":            self.constant.TYPE_INT,  # 认证方式，0:不启用员工认证, 1:邮箱认证, 2:自定义认证, 3:姓名手机号认证, 4:邮箱自定义两种认证
            "auth_code":            self.constant.TYPE_STRING,  # 认证码（6到20位， 字母和数字组成，区分大小写），默认为空
            "custom":               self.constant.TYPE_STRING,  # 配置的自定义认证名称
            "questions":            self.constant.TYPE_JSON,  # 问答列表(json)
            "custom_hint":          self.constant.TYPE_STRING,  # 自定义认证提示
        }
