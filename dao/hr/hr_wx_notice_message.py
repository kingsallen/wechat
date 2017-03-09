# coding=utf-8

# @Time    : 10/27/16 12:13
# @Author  : panda (panyuxin@moseeker.com)
# @File    : hr_wx_notice_message.py
# @DES     : 微信消息通知, first和remark文案暂不使用

from dao.base import BaseDao

class HrWxNoticeMessageDao(BaseDao):

    def __init__(self):
        super(HrWxNoticeMessageDao, self).__init__()
        self.table = "hr_wx_notice_message"
        self.fields_map = {
            "id":          self.constant.TYPE_INT,
            "wechat_id":   self.constant.TYPE_INT, # 所属公众号
            "notice_id":   self.constant.TYPE_INT, # 消息模板类型 id
            "first":       self.constant.TYPE_STRING, # 消息模板first文案
            "remark":      self.constant.TYPE_STRING,  # 消息模板remark文案
            "status":      self.constant.TYPE_INT,  # 是否开启, 1:开启, 0:关闭
        }
