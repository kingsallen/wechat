# coding=utf-8

# @Time    : 4/25/17 14:41
# @Author  : panda (panyuxin@moseeker.com)
# @File    : campaign_recommend_company.py
# @DES     :


from dao.base import BaseDao

class CampaignRecommendCompanyDao(BaseDao):

    def __init__(self):
        super(CampaignRecommendCompanyDao, self).__init__()
        self.table = "campaign_recommend_company"
        self.fields_map = {
            "id":           self.constant.TYPE_INT,
            "company_id":   self.constant.TYPE_INT,
            "weight":       self.constant.TYPE_INT,
            "disable":      self.constant.TYPE_INT,
            "create_time":  self.constant.TYPE_TIMESTAMP,
            "update_time":  self.constant.TYPE_TIMESTAMP,
        }
