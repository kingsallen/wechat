# coding=utf-8

from schematics.models import Model
from schematics.types import StringType, IntType


class UserCreationForm(Model):
    """
    在调用基础服务做用户创建时做强校验
    """

    class Options:
        serialize_when_none = True

    username = StringType(required=True)
    password = StringType(required=True)
    mobile = IntType(required=True)
    email = StringType(default='')
    register_ip = StringType(required=True)
