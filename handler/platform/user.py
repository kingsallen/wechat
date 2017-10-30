# coding=utf-8

"""这个模块主要是给数据组 AI 项目收集数据使用的
"""

from tornado import gen

import conf.path as path
import util.common.decorator as decorator
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.mq import data_userprofile_publisher


class UserSurveyConstantMixin(object):

    constant = ObjectDict()

    constant.job_grade = {
        1: "总监",
        2: "经理",
        3: "主管",
        4: "支援",
        5: "实习生"
    }

    constant.industry = {
        1:  "计算机/互联网/通信/电子",
        2:  "会计/金融/银行/保险",
        3:  "贸易/消费/制造/营运",
        4:  "制药/医疗",
        5:  "生产/加工/制造",
        6:  "广告/媒体",
        7:  "房地产/建筑",
        8:  "专业服务/教育/培训",
        9:  "服务业",
        10: "物流/运输",
        11: "能源/原材料",
        12: "政府/非赢利机构/其他"
    }

    constant.work_age = {
        1: "应届毕业生",
        2: "1-3年",
        3: "4-6年",
        4: "7-10年",
        5: "10年以上"
    }

    constant.salary = {
        1: "2K以下",
        2: "2k-4k",
        3: "4k-6k",
        4: "6k-8k",
        5: "8k-10k",
        6: "10k-15k",
        7: "15k-25k",
        8: "25k及以上"
    }

    constant.degree = {
        1: '初中及以下',
        2: '中专',
        3: '高中',
        4: '大专',
        5: '本科',
        6: '硕士',
        7: '博士',
        8: '博士以上',
        9: '其他'
    }

    @staticmethod
    def listify_dict(input_dict):
        return [[v, k] for k, v in input_dict.items()]


class UserSurveyHandler(UserSurveyConstantMixin, BaseHandler):

    @decorator.handle_response
    @decorator.authenticated
    @gen.coroutine
    def get(self):
        """直接给数据组提供数据来源，数据字典写死就好，似乎没有必要存到 dict_constant 里去
        """
        data = ObjectDict()

        data.constant = {
            'job_grade': self.listify_dict(self.constant.job_grade),
            'industry':  self.listify_dict(self.constant.industry),
            'work_age':  self.listify_dict(self.constant.work_age),
            'salary':    self.listify_dict(self.constant.salary),
            'degree':    self.listify_dict(self.constant.degree)
        }
        self.render_page('adjunct/user-survey.html', data=data)


class APIUserSurveyHandler(UserSurveyConstantMixin, BaseHandler):

    @decorator.handle_response
    @decorator.authenticated
    @gen.coroutine
    def post(self):
        """获取前端传过来的数据，POST json string格式"""

        model_raw = self.json_args.model
        self.logger.debug("model_raw: %s" % model_raw)

        model = self.process_model_raw(model_raw)
        self.logger.debug("model: %s" % model)

        self.logger.debug('pushed to rebbitmq')

        data_userprofile_publisher.publish_message(message=model)

        self.send_json_success(data={
            'next_url': self.make_url(path.PROFILE_VIEW, self.params)
        })

    def process_model_raw(self, model_raw):
        model = model_raw
        for key in model:
            if key in self.constant:
                model[key] = getattr(self.constant, key).get(model[key])
        return model
