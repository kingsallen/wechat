# coding=utf-8

from dao.base import BaseDao


class CandidateCompanyDao(BaseDao):
    def __init__(self):
        super(CandidateCompanyDao, self).__init__()
        self.table = "candidate_company"
        self.fields_map = {
            "id":               self.constant.TYPE_INT,
            "company_id":       self.constant.TYPE_INT, # hr_company.id
            "update_time":      self.constant.TYPE_TIMESTAMP, # 修改时间
            "wxuser_id":        self.constant.TYPE_INT, # user_wx_user.id  候选人绑定的user_wx_user.id，现在已经废弃。微信账号由C端账号替换，请参考sys_user_id
            "status":           self.constant.TYPE_INT, # 候选人状态，0：删除，1：正常状态
            "is_recommend":     self.constant.TYPE_INT, # 是否推荐 false:未推荐，true:推荐
            "name":             self.constant.TYPE_STRING, # user_user.name 姓名或微信昵称
            "email":            self.constant.TYPE_STRING, # sys_user.email 邮箱
            "mobile":           self.constant.TYPE_STRING, # sys_user.mobile 电话
            "nickname":         self.constant.TYPE_STRING, # user_wx_user.nickname 用户昵称
            "headimgurl":       self.constant.TYPE_STRING, # user_wx_user.headimgurl 用户头像
            "sys_user_id":      self.constant.TYPE_INT, # userdb.user_user.id C端账号编号，表示该候选人绑定的C端账号
            "click_from":       self.constant.TYPE_INT, # 来自, 0:未知, 朋友圈(timeline ) 1, 微信群(groupmessage) 2, 个人消息(singlemessage)
        }
