# coding=utf-8


from dao.base import BaseDao


class HrEmployeeCustomFieldsDao(BaseDao):

    def __init__(self):
        super(HrEmployeeCustomFieldsDao, self).__init__()
        self.table = "hr_employee_custom_fields"
        self.fields_map = {
            "id":          self.constant.TYPE_INT,
            "company_id":  self.constant.TYPE_INT,
            "fname":       self.constant.TYPE_STRING,
            "fvalues":     self.constant.TYPE_STRING,
            "forder":      self.constant.TYPE_INT,
            "disable":     self.constant.TYPE_INT,
            "mandatory":   self.constant.TYPE_INT,
            "status":      self.constant.TYPE_INT
        }
