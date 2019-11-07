# coding=utf-8

# @Time    : 17/4/17 16:13
# @Author  : panda (panyuxin@moseeker.com)
# @File    : es.py
# @DES     : elasticsearch 方法封装

import ujson
from elasticsearch import Elasticsearch

from setting import settings
from util.common import ObjectDict
from util.tool.json_tool import json_dumps
from util.tool.dict_tool import objectdictify
from util.tool.es_tool import init_gamma_basic, rule_gamma_filters


class BaseES(object):
    """es客户端设置为嗅探模式,保证程序的可用性,sniff 来进行集群探测。
    创建对象的时候，引入n个节点，如果一个节点挂掉，对于程序没有影响。
    http://elasticsearch-py.readthedocs.io/en/master/"""
    _es = Elasticsearch(settings['es_client'],
                        sniff_on_start=True,
                        sniff_on_connection_fail=True,
                        sniffer_timeout=60
                        )

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            orig = super(BaseES, cls)
            cls._instance = orig.__new__(cls, *args, **kwargs)
        return cls._instance

    def get_raw_es_client(self):
        return self._es

    def search(self, index=None, doc_type=None, body=None, timeout=10):

        result = self._es.search(index, doc_type, json_dumps(body), request_timeout=timeout)
        return objectdictify(result)


if __name__ == "__main__":

    es = BaseES()

    params = ObjectDict({
        "salary_top": 0,
        "salary_bottom": 0,
        "salary_negotiable": 1,
        "keywords": "开发,产品",
        "city": "上海,北京",
        "industry": "互联网"
    })

    params = rule_gamma_filters(params)
    print(params)

    body = init_gamma_basic(params.keywords,
                                  params.city,
                                  params.industry,
                                  params.salary_bottom,
                                  params.salary_top,
                                  params.salary_negotiable, 0, 10)

    # print(body)
    print(ujson.dumps(body))

    res = es.search(index="positions", body=body)
    print(res)
