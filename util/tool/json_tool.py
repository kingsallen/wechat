# coding: utf-8

import datetime
import decimal
import json


class JSONEncoder(json.JSONEncoder):
    """指定非内置 JSON serializable 的类型应该如何转换

    不符合JSON规范的类型包括：
    decimal.Decimal,
    datetime.datetime,
    datetime.date

    请酌情添加
    """
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        elif isinstance(o, datetime.datetime):
            return o.__str__()
        elif isinstance(o, datetime.date):
            return o.__str__()
        elif isinstance(o, bytes):
            return str(o)

        return json.JSONEncoder.default(self, o)


def json_dumps(obj, ensuer_ascii=False):
    """用于将含有不符合 JSON 规范的类型的 dict 对象序列化，
    使用自定义的 JSONEncoder
    :param obj: 需要 dumps 的对象
    :param ensuer_ascii: 是否使用 ascii 字符表示 unicode char， 默认为 False
    :return: 序列化后的 str
    """
    ret = json.dumps(obj, cls=JSONEncoder, ensure_ascii=ensuer_ascii)

    # 对于 '/' 的处理参考 tornado 的实现
    # 由于没有直接封装 tornado.escape.json_encode， 所以需要对此进行额外处理
    # ref: https://github.com/tornadoweb/tornado/blob/master/tornado/escape.py#L74-L82
    return ret.replace("</", "<\\/")


def encode_json_dumps(obj):
    """对对象进行两次dump
    主要用于 render json,也在封装职位信息时使用
    """
    # 先用 json_dumps 处理可能异常的数据，再用 json.dumps 来再次序列化
    return json.dumps(json_dumps(obj))
