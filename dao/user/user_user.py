# coding=utf-8

from dao.base import BaseDao


class UserUserDao(BaseDao):
    def __init__(self):
        super(UserUserDao, self).__init__()
        self.table = "user_user"
        self.fields_map = {
            "id"              :self.constant.TYPE_INT,
            "username"        :self.constant.TYPE_STRING,
            "password"        :self.constant.TYPE_STRING,
            "is_disable"      :self.constant.TYPE_INT,
            "rank"            :self.constant.TYPE_INT,
            "register_time"   :self.constant.TYPE_TIMESTAMP,
            "register_ip"     :self.constant.TYPE_STRING,
            "last_login_time" :self.constant.TYPE_TIMESTAMP,
            "last_login_ip"   :self.constant.TYPE_STRING,
            "login_count"     :self.constant.TYPE_INT,
            "mobile"          :self.constant.TYPE_INT,
            "email"           :self.constant.TYPE_STRING,
            "activation"      :self.constant.TYPE_INT,
            "activation_code" :self.constant.TYPE_STRING,
            "token"           :self.constant.TYPE_STRING,
            "name"            :self.constant.TYPE_STRING,
            "headimg"         :self.constant.TYPE_STRING,
            "national_code_id":self.constant.TYPE_INT,
            "wechat_id"       :self.constant.TYPE_INT,
            "unionid"         :self.constant.TYPE_STRING,
            "source"          :self.constant.TYPE_INT,
            "company"         :self.constant.TYPE_STRING,
            "position"        :self.constant.TYPE_STRING,
            "parentid"        :self.constant.TYPE_INT,
            "nickname"        :self.constant.TYPE_STRING,
            "email_verified"  :self.constant.TYPE_INT,
        }
