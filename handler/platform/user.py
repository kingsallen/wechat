# coding=utf-8

"""这个模块主要是给数据组 AI 项目收集数据使用的
"""

from handler.base import BaseHandler
import util.common.decorator as decorator
from util.common import ObjectDict

from tornado import gen


class UserSurveyHandler(BaseHandler):

    @decorator.handle_response
    @decorator.authenticated
    @gen.coroutine
    def get(self):
        """直接给数据组提供数据来源，数据字典写死就好，似乎没有必要存到 dict_constant 里去
        """

        constant = ObjectDict()

        constant.job_grade = [["总监", 1], ["经理", 2], ["主管", 3], ["支援", 4],
                              ["实习生", 5]]

        constant.industry = [["计算机/互联网/通信/电子", 1], ["会计/金融/银行/保险", 2],
                             ["贸易/消费/制造/营运", 3],
                             ["制药/医疗", 4], ["生产/加工/制造", 5], ["广告/媒体", 6],
                             ["房地产/建筑", 7],
                             ["专业服务/教育/培训", 8], ["服务业", 9], ["物流/运输", 10],
                             ["能源/原材料", 11],
                             ["政府/非赢利机构/其他", 12]]

        constant.age = [["20-30岁", 1], ["30-40岁", 2], ["40-50岁", 3],
                        ["50岁以上", 4]]

        constant.work_age = [["应届毕业生", 1], ["1-3年", 2], ["4-6年", 3],
                             ["7-10年", 4],
                             ["10年以上", 5]]

        constant.salary = [["2K以下", 1], ["2k-4k", 2], ["4k-6k", 3],
                           ["6k-8k", 4],
                           ["8k-10k", 5], ["10k-15k", 6], ["15k-25k", 7],
                           ["25k及以上", 8]]

        constant.degree = [['初中及以下', 1], ['中专', 2], ['高中', 3], ['大专', 4],
                           ['本科', 5], ['硕士', 6], ['博士', 7], ['博士以上', 8],
                           ['其他', 9]]

        data = ObjectDict()

        data.constant = constant

        self.render_page('adjunctuser-survey.html', data=data)


class APIUserSurveyHandler(BaseHandler):
    @decorator.handle_response
    @decorator.authenticated
    @gen.coroutine
    def post(self):
        """获取前端传过来的数据，POST json string格式"""

        # model: {
        #     job_grade: 3,
        #     industry:  2,
        #     birth:     '2017-10-10',
        #     degree:    3,
        #     work_age:  1,
        #     city:      '上海',
        #     salary:    3,
        # }

        model = self.json_args.model

        self.logger.debug("model: %s" % model)
        # todo tangyiliang
        # push the message to rabbitmq
        self.logger.debug('pushed to rebbitmq')

        self.redirect_to_route('position_list', self.params)
