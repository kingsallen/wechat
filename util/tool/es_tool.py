# coding=utf-8

# @Time    : 4/18/17 15:06
# @Author  : panda (panyuxin@moseeker.com)
# @File    : es_tool.py
# @DES     : 初始化 ES 搜索字段

import re
from util.common import ObjectDict

def rule_gamma_filters(params):
    ''' 筛选条件, 转成相应的类型, 及对用户的输入进行过滤 '''

    # 需要int
    for k in ('salary_top', 'salary_bottom', 'salary_negotiable'):
        if params.get(k):  params[k] = int(params[k])

    # 需要 list
    for k in ('industry', 'city'):
        if params.get(k):
            params[k] = re.split(",", params[k].strip())
        else:
            params[k] = list()
    # 需要用 OR 串联
    for k in ('keywords'):
        if params.get(k):
            k_list = re.split(",", params[k].strip())
            params[k] = " OR ".join(k_list)
        else:
            params[k] = ""

    return params

def init_gamma_basic_agg(query, city, industry, salary_bottom, salary_top, salary_negotiable, page_from, page_size):

    """
    初始化 Gamma 项目列表页搜索
    详情查看: https://wiki.moseeker.com/gamma_0.9_es.md
    :return:
    """

    init_es_query = {
        "query": {
            "bool": {
                "must": [{
                    "query_string": {
                        "fields": [
                            {
                                "field": "position.title",
                                "boost": 20.0
                            },
                            {
                                "field": "position.city",
                                "boost": 10.0
                            },
                            {
                                "field": "company.name",
                                "boost": 5.0
                            },
                            {
                                "field": "company.abbreviation",
                                "boost": 10.0
                            },
                            {
                                "field": "team.name",
                                "boost": 7.0
                            },
                            {
                                "field": "company.introduction",
                                "boost": 2.0
                            },
                            {
                                "field": "position.requirement",
                                "boost": 5.0
                            },
                            {
                                "field": "position.occupation",
                                "boost": 2.0
                            },
                            {
                                "field": "position.accountabilities",
                                "boost": 5.0
                            }
                        ],
                        "query": query
                    }
                },
                {
                    "terms": {
                        "position.city": city,
                    }
                },
                {
                    "terms": {
                        "position.industry": industry,
                    }
                }
                ],
                "filter": {
                    "script": {
                        "script":
                            "min=0;max=1000;"
                            "bottom=_source.position.salary_bottom;"
                            "top=_source.position.salary_top;"
                            "if(min>bottom&&min<top&&top>bottom){return true;};"
                            "if(max<top&&max>bottom&&top>bottom){return true;};"
                            "if(min<bottom&&max>top&&top>bottom){return true;};"
                            "if(bottom==0&&top==0){return true;};"
                            "return false"
                    }
                }
            }
        },
        "track_scores": "true",
        "sort": {
            "_script": {
                "type": "number",
                "script": {
                    "inline": "score =_score;"
                              "spell=_source.spell;"
                              "if(spell<4&&spell>0){score=score*1.1}"
                              "else if(spell>=4&&spell<7){score=score}"
                              "else if(spell>=7&&spell<10){score=score*0.8}"
                              "else if(spell>=10&&spell<13){score=score*0.5}"
                              "else {score=score*0.1};"
                              "return score;"
                },
                "order": "desc"
            }
        },
        "from": page_from,
        "size": page_size
    }

    return init_es_query
