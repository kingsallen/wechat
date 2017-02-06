# coding=utf-8

from dao.base import BaseDao


class UserFavPositionDao(BaseDao):
    def __init__(self):
        super(UserFavPositionDao, self).__init__()
        self.table = "user_fav_position"
        self.fields_map = {
            'sysuser_id':  self.constant.TYPE_INT,
            'position_id': self.constant.TYPE_INT,
            'favorite':    self.constant.TYPE_INT,  # 0:收藏, 1:取消收藏, 2:感兴趣
            'create_time': self.constant.TYPE_TIMESTAMP,
            'update_time': self.constant.TYPE_TIMESTAMP,
            'mobile':      self.constant.TYPE_STRING,
            'id':          self.constant.TYPE_INT,
            'wxuser_id':   self.constant.TYPE_INT,
            'recom_id':    self.constant.TYPE_INT,
        }
