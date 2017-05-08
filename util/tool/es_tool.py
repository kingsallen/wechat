# coding=utf-8

# @Time    : 4/18/17 15:06
# @Author  : panda (panyuxin@moseeker.com)
# @File    : es_tool.py
# @DES     : 初始化 ES 搜索字段

import re
from util.common import ObjectDict
from util.tool.str_tool import split

def rule_gamma_filters(params):

    ''' 筛选条件, 转成相应的类型, 及对用户的输入进行过滤 '''

    # 需要 list
    for k in ('industry', 'city'):
        if params.get(k):
            params[k] = split(params[k].strip(), [","])
        else:
            params[k] = list()

    # 需要用 OR 串联
    for k in ('keywords',):
        if params.get(k):
            k_list = re.split(",", params[k].strip())
            params[k] = " OR ".join(k_list)
        else:
            params[k] = ""

    return params

def init_gamma_basic(query, city, industry, salary_bottom, salary_top, salary_negotiable, page_from, page_size):

    """
    初始化 Gamma 项目列表页搜索
    详情查看: https://wiki.moseeker.com/gamma_0.9_es.md
    :return:
    """

    init_es_query = ObjectDict({
        "query": ObjectDict({
            "bool": ObjectDict({
                "must": []
            })
        }),
        "track_scores": "true",
        "sort": ObjectDict({
            "_script": ObjectDict({
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
            })
        }),
        "aggs": ObjectDict({
            "all_count": ObjectDict({
                "scripted_metric": ObjectDict({
                    "init_script": "_agg['transactions'] = []",
                    "map_script": "banner=_source.company.banner;impression=_source.company.impression;company_id = _source.position.company_id; "
                                  "if(banner!=''&&impression!=''&&company_id  in _agg['transactions'] ){}else{_agg['transactions'].add(company_id)};",
                    "reduce_script": "jsay=[];for(a in _aggs){for(ss in a){if(ss in jsay){}else{jsay.add(ss);}}};return jsay",
                    "combine_script": "jsay=[];for(a in _agg['transactions']){for(ss in a){jsay.add(ss)}};return jsay"
                })
            })
        }),

        "from": page_from,
        "size": page_size
    })

    if query:
        # 存在搜索关键字
        query_sql = ObjectDict({
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
        })
        init_es_query['query']['bool']['must'].append(query_sql)

    if city:
        # 存在城市筛选
        init_es_query['query']['bool']['must'].append(ObjectDict({
            "terms": {
                "position.city": city,
            }
        }))

    if industry:
        # 存在行业筛选
        init_es_query['query']['bool']['must'].append(ObjectDict({
            "terms": {
                "company.industry_type_name": industry,
            }
        }))

    if (isinstance(salary_bottom, int) and isinstance(salary_top, int)) or salary_negotiable:
        # 存在薪资上下限
        # 存在行业筛选
        min_max = """min=0;max=1000;"""
        condition = "if(min>bottom&&min<top&&top>bottom){return true;};" \
                 "if(max<top&&max>bottom&&top>bottom){return true;};" \
                 "if(min<bottom&&max>top&&top>bottom){return true;};"
        negotiable = """if(bottom==0&&top==0){return true;};"""
        filter_script = "{}bottom=_source.position.salary_bottom;" \
                        "top=_source.position.salary_top;{}{}return false"

        if isinstance(salary_bottom, int) and isinstance(salary_top, int) and not salary_negotiable:
            script = filter_script.format(min_max, condition, "")
        elif isinstance(salary_bottom, int) and isinstance(salary_top, int) and salary_negotiable:
            script = filter_script.format(min_max, condition, negotiable)
        else:
            script = filter_script.format("", "", negotiable)

        init_es_query['query']['bool'].update(ObjectDict({
            "filter": ObjectDict({
                "script": ObjectDict({
                    "script": script
                })
            })
        }))

    return init_es_query
