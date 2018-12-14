# coding=utf-8

from tornado import gen

import conf.common as const
import conf.message as msg
import conf.path as path
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated, check_employee_common


class RadarDemoHandler(BaseHandler):
    """产品发布会使用的雷达的demo"""

    @gen.coroutine
    def get(self):
        self.render_page(template_name="radar/index.html", data=ObjectDict())


class RadarDemoApiHandler(BaseHandler):
    """雷达demo数据"""

    @gen.coroutine
    def get(self):
        num = int(self.params.num) - 5
        position_id = self.params.position_id
        position = yield self.position_ps.get_position(position_id=position_id)
        record = yield self.sharechain_ps.find_candidate_by_position(position_id=position_id, num=num)

        hack_data = [
            {
                "id": 111111,
                "name": "陈迪",
                "headimg": "http://thirdwx.qlogo.cn/mmopen/Q3auHgzwzM5bdNZA3dQ6Ddj47omFnwC9oZTDy1ibpOmOg2LsQKE5291EHaddBKOkeicakiaNrb1XQF7jJfWBkJzog/132",
                "is_hack": True,
                "viewnum": 9,
                "click_from": 2,
                "click_time": "2018-12-20 07:12:43",
                "position_title": "{}".format(position.title)},
            {
                "id": 111112,
                "name": "Towry",
                "headimg": "https://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTJ1Q15bKpUb0vXGCgLjYHpiaBDGZohOrqh1TUKvS1IAusibRtk6mUWF6AMcLfjReHz2O3uO4XJWVcpw/132",
                "is_hack": True,
                "viewnum": 3,
                "click_from": 1,
                "click_time": "2018-12-20 08:32:46",
                "position_title": "{}".format(position.title)
            },
            {
                "id": 111113,
                "name": "Sunny",
                "headimg": "https://thirdwx.qlogo.cn/mmopen/vi_32/8hN3qjD08YAmwiashKFhZQEN18WaqaKQygThnSWpNicYIZroucggHxm2x3pk6TMtnOzQh3WpBvIGXHpd6mwXiag7w/132",
                "is_hack": True,
                "viewnum": 2,
                "click_from": 1,
                "click_time": "2018-12-20 08:45:32",
                "position_title": "{}".format(position.title)
            },
            {
                "id": 111114,
                "name": "Jack Weng",
                "headimg": "https://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTK3HJD1CfyeTuJpSgUK2p2aVGd4FA2BXIiaTvmxcyWrzbsEUhb532ZNP0pMEAz3BUPl8PAh9jRnweg/132",
                "is_hack": True,
                "viewnum": 4,
                "click_from": 3,
                "click_time": "2018-12-20 08:20:33",
                "position_title": "{}".format(position.title)
            },
            {
                "id": 111115,
                "name": "Neil",
                "headimg": "https://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTLMcEQkPTX3gF6bodiat42ic4u3icSkia8iaYlFOo5NS4E3tiap5UDEsCZHgo2Rww2MmKl5pvkC9n7icWtIQ/132",
                "is_hack": True,
                "viewnum": 1,
                "click_from": 3,
                "click_time": "2018-12-20 08:11:15",
                "position_title": "{}".format(position.title)
            },
        ]

        record = hack_data + record
        self.send_json_success(record)
