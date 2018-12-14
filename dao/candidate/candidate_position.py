# coding=utf-8

from dao.base import BaseDao


class CandidatePositionDao(BaseDao):
    def __init__(self):
        super(CandidatePositionDao, self).__init__()
        self.table = "candidate_position"
        self.fields_map = {
            "position_id":               self.constant.TYPE_INT,
            "candidate_company_id":      self.constant.TYPE_INT,  # candidate_company_id
            "update_time":               self.constant.TYPE_TIMESTAMP,  # 修改时间
            "wxuser_id":                 self.constant.TYPE_INT,  # user_wx_user.id  候选人绑定的user_wx_user.id，现在已经废弃。微信账号由C端账号替换，请参考sys_user_id
            "is_interested":             self.constant.TYPE_INT,  # 是否感兴趣
            "view_number":               self.constant.TYPE_INT,
            "shared_from_employee":      self.constant.TYPE_INT,
            "user_id":                   self.constant.TYPE_INT,  # userdb.user_user.id C端账号编号，表示该候选人绑定的C端账号
        }
