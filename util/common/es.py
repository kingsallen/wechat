# coding=utf-8

# @Time    : 17/4/17 16:13
# @Author  : panda (panyuxin@moseeker.com)
# @File    : es.py
# @DES     : elasticsearch 方法封装

import ujson
from elasticsearch import Elasticsearch

from setting import settings
from util.tool.json_tool import json_dumps


class BaseES(object):

    _es = Elasticsearch(settings.es)

    _INDEX = "WECHAT"

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            orig = super(BaseES, cls)
            cls._instance = orig.__new__(cls, *args, **kwargs)
        return cls._instance

    def get_raw_es_client(self):
        return self._es

    def search(self, index=None, doc_type=None, body=None):
        return self._es.search(index, doc_type, json_dumps(body))


if __name__ == "__main__":

    es = BaseES()
    body = {
        "query": {
            "match": {
                "position.title":"项目及大客户销售工程师"
            }
        },
        "from": 0,
        "size": 10000
    }

    res = es.search(index="positions", body=body)
    print (type(res))
    print (res.get("position"))
