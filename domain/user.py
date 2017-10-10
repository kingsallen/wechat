# coding=utf-8

import re

from schematics.models import Model
from schematics.types import StringType, IntType
from schematics.exceptions import ValidationError


class DateStringType(StringType):
    """日期格式字符串"""
    date_format = r'^\d{4}\-\d{2}\-\d{2}$'

    def validate_format(self, value):
        if not re.match(self.date_format, value):
            raise ValidationError(u'不是日期格式!')


class UserCreationForm(Model):
    """
    在调用基础服务做用户创建时做强校验
    """

    class Options:
        serialize_when_none = True

    username = StringType(required=True)
    password = StringType(required=True)
    country_code = StringType(required=True)
    mobile = IntType(required=True)
    email = StringType(default='')
    register_ip = StringType(required=True)
    register_time = StringType(required=True)


class InterestCurrentInfoForm(Model):
    """我感兴趣填写目前在职信息时使用"""

    name = StringType(required=True)
    company = StringType(required=True)
    position = StringType(required=True)
    start_date = DateStringType(required=True)
