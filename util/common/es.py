# coding=utf-8

# @Time    : 17/4/17 16:13
# @Author  : panda (panyuxin@moseeker.com)
# @File    : es.py
# @DES     : elasticsearch 方法封装

from elasticsearch import Elasticsearch

from setting import settings


class BaseES(object):

    _es = Elasticsearch(settings.es)

    _INDEX = "WECHAT"

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            orig = super(BaseES, cls)
            cls._instance = orig.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, methods=('search')):
        for method_name in methods:
            assert hasattr(self, method_name)

    def get_raw_es_client(self):
        return self._es

    def search(self, index=None, doc_type=None, body=None, params=None):
        return self._es.search(index, doc_type, body, params)


if __name__ == "__main__":

    es = BaseES()

    res = es.search()
