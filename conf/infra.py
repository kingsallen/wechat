# coding=utf-8

import enum


@enum.unique
class InfraStatusCode(enum.IntEnum):

    normal = 0
    not_exist = 90010

