# coding=utf-8

# Copyright 2016 MoSeeker

"""
:author 潘煜昕（panyuxin@moseeker.com）
:date 2016.07.26
:table hr_wx_wechat

"""

from dao.base import BaseDao


class HrWxWechatDao(BaseDao):

    def __init__(self, logger):
        super(HrWxWechatDao, self).__init__(logger)
        self.table = "hr_wx_wechat"
        self.fields_map = {
            "id":              self.constant.TYPE_INT,
            "company_id":      self.constant.TYPE_INT, # 所属公司id, hr_company.id
            "type":            self.constant.TYPE_INT, # 公众号类型, 0:订阅号, 1:服务号
            "signature":       self.constant.TYPE_STRING, # 公众号ID匿名化
            "name":            self.constant.TYPE_STRING, # 名称
            # "alias":          self.constant.TYPE_STRING, # 别名
            # "username":       self.constant.TYPE_STRING, # 用户名
            # "password":       self.constant.TYPE_STRING, # 密码
            # "token":          self.constant.TYPE_STRING, # 开发者token
            "appid":           self.constant.TYPE_STRING, # 开发者appid
            "secret":          self.constant.TYPE_STRING, # 开发者secret
            # "welcome":        self.constant.TYPE_INT, # welcome message
            # "default":        self.constant.TYPE_INT, # default message
            "qrcode":          self.constant.TYPE_STRING, # 关注公众号的二维码
            "third_oauth":     self.constant.TYPE_INT, # 授权大岂第三方平台0：未授权 1：授权了
            "passive_seeker":  self.constant.TYPE_INT, # 被动求职者开关，0：开启，1：不开启
            "hr_register":     self.constant.TYPE_INT, # 是否启用免费雇主注册，0：不启用，1：启用
            "hr_chat":         self.constant.TYPE_INT, # IM聊天开关，0：不开启，1：开启
            # "access_token_create_time": self.constant.TYPE_INT, # access_token最新更新时间
            # "access_token_expired": self.constant.TYPE_INT, # access_token过期时间
            "access_token":    self.constant.TYPE_STRING, # access_token
            "jsapi_ticket":    self.constant.TYPE_STRING, # jsapi_ticket
            "authorized":      self.constant.TYPE_INT, # 是否授权0：无关，1：授权2：解除授权
            # "authorizer_refresh_token": self.constant.TYPE_STRING, # 第三方授权的刷新token，用来刷access_token
            "create_time":     self.constant.TYPE_TIMESTAMP, # 创建时间
            "update_time":     self.constant.TYPE_TIMESTAMP, # 更新时间
        }
