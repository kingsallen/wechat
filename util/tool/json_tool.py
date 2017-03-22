# coding: utf-8

import datetime
import decimal
import json


class JSONEncoder(json.JSONEncoder):
    """指定非内置 JSON serializable 的类型应该如何转换
    """
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        elif isinstance(o, datetime.datetime):
            return o.__str__()
        elif isinstance(o, datetime.date):
            return o.__str__()
        return json.JSONEncoder.default(self, o)


def json_dumps(obj):
    """用于将含有不符合 JSON 规范的类型的 dict 对象序列化，
    使用自定义的 JSONEncoder。
    不符合JSON规范的类型包括： decimal.Decimal, datetime.datetime, datetime.date

    不要直接使用此方法除非有明确的理由
    """
    return json.dumps(obj, cls=JSONEncoder, ensure_ascii=False)


def encode_json_dumps(obj):
    """对对象进行两次dump
    主要用于 render json, 也在封装职位信息时使用
    """
    return json.dumps(json_dumps(obj))
