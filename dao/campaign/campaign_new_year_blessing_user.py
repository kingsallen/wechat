# coding=utf-8

# Copyright 2018 MoSeeker

from dao.base import BaseDao


class CampaignNewYearBlessingUserDao(BaseDao):

    def __init__(self):
        super(CampaignNewYearBlessingUserDao, self).__init__()
        self.table = "campaign_new_year_blessing_user"
        self.fields_map = {
            "id":                       self.constant.TYPE_INT,
            "company_id":               self.constant.TYPE_INT,  # hr_company.id
            "employee_id":              self.constant.TYPE_INT,  # hr_employee.id
            "sysuser_id":               self.constant.TYPE_INT,  # user_user.id, C端用户ID
            "name":                     self.constant.TYPE_STRING,  # 姓名
            "company_name":             self.constant.TYPE_STRING,  # 公司注册名称
            "wx_openid":                self.constant.TYPE_STRING,  # 用户标示
            "qx_openid":                self.constant.TYPE_STRING,  # 聚合号用户标示
            "binding_time":             self.constant.TYPE_TIMESTAMP,  # 认证时间
            "employee_count":           self.constant.TYPE_INT,  # 所属公司员工数量
            "share_position_count":     self.constant.TYPE_INT,  # 分享职位的数量
            "viewing_count":            self.constant.TYPE_INT,  # 浏览了分享的职位的人数
            "recommend_talent_count":   self.constant.TYPE_INT,  # 推荐人才个数
            "has_integral_config":      self.constant.TYPE_INT,  # 所属公司是否有积分配置
            "integrals":                self.constant.TYPE_INT,  # 积分
            "has_redpacket_activity":   self.constant.TYPE_INT,  # 所属公司是否有红包活动
            "redpacket_count":          self.constant.TYPE_INT,  # 红包个数
            "is_send":                  self.constant.TYPE_INT,  # 是否发送消息模板
            "activity_batch":           self.constant.TYPE_INT,  # 活动批次
            "create_time":              self.constant.TYPE_TIMESTAMP,  # 创建时间
            "update_time":              self.constant.TYPE_TIMESTAMP,  # 更新时间
        }
