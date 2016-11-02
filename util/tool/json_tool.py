# coding: utf-8

# Copyright 2016 MoSeeker

import datetime
import decimal
import json
import ujson  # for encode json first time


class JSONEncoder(json.JSONEncoder):

    """
    指定非内置 JSON serializable 的类型应该如何转换
    """
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, datetime.datetime):
            return o.__str__()
        if isinstance(o, datetime.date):
            return o.__str__()
        return json.JSONEncoder.default(self, o)


def json_dumps(p_dict):
    if not (isinstance(p_dict, dict) or isinstance(p_dict, list)):
        raise ValueError("p_dict is not a required instance.")
    return JSONEncoder().encode(p_dict)


def encode_json_dumps(p_dict):
    if not isinstance(p_dict, dict):
        raise ValueError("p_dict is not a dict instance.")
    return json.dumps(ujson.dumps(p_dict), cls=JSONEncoder)


if __name__ == '__main__':

    print (json_dumps({
        "status": 0,
        "message": "success",
        "data": 0
    }))

