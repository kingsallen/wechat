# -*- coding=utf-8 -*-
# Copyright 2017 MoSeeker

"""
:author 陈迪（chendi@moseeker.com）
:date 2017.03.26
"""

from collections import defaultdict

def group(l, key):
    """

    :param l:
    :param key:
    :return:
    """
    d = defaultdict(list)
    for item in l:
        d[item[key]].append(item)
    return d

if __name__ == "__main__":
    m1 = {"name": "m1", "id": 1}
    m2 = {"name": "m2", "id": 2}
    m3 = {"name": "m3", "id": 3}
    m4 = {"name": "m4", "id": 3}
    m5 = {"name": "m5", "id": 3}
    m6 = {"name": "m6", "id": 1}
    m = [m1, m2, m3, m4, m5, m6]
    l = group(m, "id")
    from pprint import pprint
    pprint(l)

