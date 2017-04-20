# coding=utf-8

# Copyright 2016 MoSeeker

import xml.etree.ElementTree as ET
from util.common import ObjectDict


def parse_msg(raw_msg):
    root = ET.fromstring(raw_msg)
    msg = ObjectDict()
    for child in root:
        msg[child.tag] = child.text
    return msg
