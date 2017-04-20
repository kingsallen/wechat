# coding=utf-8

# Copyright 2016 MoSeeker

from dao.base import BaseDao


class CampaignEmailAgentdeliveryDao(BaseDao):

    def __init__(self):
        super(CampaignEmailAgentdeliveryDao, self).__init__()
        self.table = "campaign_email_agentdelivery"
        self.fields_map = {
            "id":            self.constant.TYPE_INT,
            "company_id":    self.constant.TYPE_INT, # hr_company.id
            "position_id":   self.constant.TYPE_INT, # job_position.id
            "employee_id":   self.constant.TYPE_INT, # hr_employee.id
            "friendname":    self.constant.TYPE_STRING, # 推荐朋友姓名
            "email":         self.constant.TYPE_STRING, # 推荐朋友的邮箱
            "status":        self.constant.TYPE_INT,  # 该条记录的状态
            "fname":         self.constant.TYPE_STRING, # 附件原始名称
            "uname":         self.constant.TYPE_STRING, # 附件存储名称
            "code":          self.constant.TYPE_STRING, # 发送邮件时携带的code
            "description":   self.constant.TYPE_STRING, # 上传文件描述
            "create_time":   self.constant.TYPE_TIMESTAMP, # 记录创建时间
            "update_time":   self.constant.TYPE_TIMESTAMP, # 更新时间
        }
