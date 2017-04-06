# coding=utf-8

# Copyright 2016 MoSeeker

"""
:author 潘煜昕（panyuxin@moseeker.com）
:date 2016.07.25
:table hr_company_conf

"""

from dao.base import BaseDao

class HrCompanyConfDao(BaseDao):

    def __init__(self, logger):
        super(HrCompanyConfDao, self).__init__(logger)
        self.table = "hr_company_conf"
        self.fields_map = {
            "company_id":           self.constant.TYPE_INT, # hr_company.id
            "theme_id":             self.constant.TYPE_INT, # sys_theme id
            "hb_throttle":          self.constant.TYPE_INT, # 全局每人每次红包活动可以获得的红包金额上限
            "app_reply":            self.constant.TYPE_STRING, # 申请提交成功回复信息
            "create_time":          self.constant.TYPE_TIMESTAMP, # 创建时间
            "update_time":          self.constant.TYPE_TIMESTAMP, # 更新时间
            "employee_binding":     self.constant.TYPE_STRING, # 员工认证自定义文案
            "recommend_presentee":  self.constant.TYPE_STRING, # 推荐候选人自定义文案
            "recommend_success":    self.constant.TYPE_STRING, # 推荐成功自定义文案
            "forward_message":      self.constant.TYPE_STRING, # 转发职位自定义文案
            "job_custom_title":     self.constant.TYPE_STRING, # 职位自定义字段标题
            "search_seq":           self.constant.TYPE_STRING, # 搜索页页面设置顺序,3#1#2
            "search_img":           self.constant.TYPE_STRING, # 搜索页页面设置背景图
            "teamname_custom":      self.constant.TYPE_STRING, # 职位部门字段名称
            "newjd_status":         self.constant.TYPE_INT,  # 新JD申请状态
            "application_time":     self.constant.TYPE_TIMESTAMP,  # 新JD开通申请时间
        }
