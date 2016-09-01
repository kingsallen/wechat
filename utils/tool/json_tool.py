# coding: utf-8

import datetime
import decimal
import json
from tornado.util import ObjectDict

class JSONEncoder(json.JSONEncoder):

    """
    指定非内置 JSON serializable 的类型应该如何转换
    """
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        if isinstance(o, datetime.date):
            return str(o)
        return json.JSONEncoder.default(self, o)

def json_dumps(p_dict):

    if not (isinstance(p_dict, dict)
            or isinstance(p_dict, list)
            or isinstance(p_dict, ObjectDict)):
        raise ValueError("p_dict is not a required instance.")

    return JSONEncoder().encode(p_dict)
