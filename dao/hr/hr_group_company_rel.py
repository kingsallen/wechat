# coding=utf-8


from dao.base import BaseDao


class HrGroupCompanyRelDao(BaseDao):
    def __init__(self):
        super(HrGroupCompanyRelDao, self).__init__()
        self.table = "hr_group_company_rel"
        self.fields_map = {
            "id":          self.constant.TYPE_INT,
            "company_id":  self.constant.TYPE_INT,
            "group_id":    self.constant.TYPE_INT,
            # 暂时不需要，有必要再解除注释
            # "create_time": self.constant.TYPE_TIMESTAMP,  # 创建时间
            # "update_time": self.constant.TYPE_TIMESTAMP  # 更新时间
        }
