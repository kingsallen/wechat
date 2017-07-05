# coding=utf-8


from dao.base import BaseDao


class UserEmployeePointsRecordCompanyRelDao(BaseDao):
    def __init__(self):
        super(UserEmployeePointsRecordCompanyRelDao, self).__init__()
        self.table = "user_employee_points_record_company_rel"
        self.fields_map = {
            'id':                        self.constant.TYPE_INT,
            'company_id':                self.constant.TYPE_INT,
            'employee_points_record_id': self.constant.TYPE_INT,
            'create_time':               self.constant.TYPE_TIMESTAMP,
            'update_time':               self.constant.TYPE_TIMESTAMP
        }
