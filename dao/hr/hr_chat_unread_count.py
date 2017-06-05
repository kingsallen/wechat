# coding=utf-8

# @Time    : 10/28/16 09:58
# @Author  : panda (panyuxin@moseeker.com)
# @File    : hr_chat_unread_count.py
# @DES     : 聊天室未读消息


from dao.base import BaseDao

class HrChatUnreadCountDao(BaseDao):

    def __init__(self):
        super(HrChatUnreadCountDao, self).__init__()
        self.table = "hr_chat_unread_count"
        self.fields_map = {
            "room_id":              self.constant.TYPE_INT,
            "hr_id":                self.constant.TYPE_INT,
            "user_id":              self.constant.TYPE_INT,
            "wx_chat_time":         self.constant.TYPE_TIMESTAMP,
            "hr_chat_time":         self.constant.TYPE_TIMESTAMP,
            "hr_have_unread_msg":   self.constant.TYPE_INT,
            "user_have_unread_msg": self.constant.TYPE_INT,

        }
