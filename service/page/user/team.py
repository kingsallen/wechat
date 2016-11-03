# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.11.1

"""
from util.common import ObjectDict
from tornado import gen
from service.page.base import PageService
# from tests.dev_data.user_company_data import WORKING_ENV, TEAMS


class TeamPageService(PageService):

    _OTHER_TEAM = ObjectDict(
        cs={
            "title": "客户成功团队",
            "link":  "https://platform.moseeker.com/m/company/team/cs?wechat_signature=NjYyM2M4ZDAzOTk5NThmNjlhMGI0OWM2ZTgwOTk1Njc2MTU0Y2ZhOQ==",
            "description": "专注于提供企业雇主品牌的策略咨询及实施服务",
            "media_url": 'https://cdn.moseeker.com/upload/company_profile/qx/'
                                   'CSFULL.png',
            "media_type": "image"
        },
        bd={
            "title":       "商务拓展团队",
            "link": "https://platform.moseeker.com/m/company/team/bd"
                    "?wechat_signature=NjYyM2M4ZDAzOTk5NThmNjlhMGI0OWM2ZTgwOTk1Njc2MTU0Y2ZhOQ==",
            "description": "开发优秀企业，提供合作方案，解决招聘难题，提升雇主形象",
            "media_url":   'https://cdn.moseeker.com/upload/company_profile/qx/'
                                   'BDFULL.jpeg',
            "media_type":  "image"
        },
        eb={
            "title":       "雇主品牌团队",
            "link": "https://platform.moseeker.com/m/company/team/eb"
                    "?wechat_signature=NjYyM2M4ZDAzOTk5NThmNjlhMGI0OWM2ZTgwOTk1Njc2MTU0Y2ZhOQ==",
            "description": "专注于提供企业雇主品牌的策略咨询及实施服务",
            "media_url":   'https://cdn.moseeker.com/upload/company_profile/qx/'
                                   'EBFULL.jpeg',
            "media_type":  "image"
        },
        rd={
            "title":       "研发团队",
            "link": "https://platform.moseeker.com/m/company/team/rd"
                    "?wechat_signature=NjYyM2M4ZDAzOTk5NThmNjlhMGI0OWM2ZTgwOTk1Njc2MTU0Y2ZhOQ==",
            "description": "仟寻招聘的技术保证和动力引擎",
            "media_url":   'https://cdn.moseeker.com/upload/company_profile/qx/'
                                   'RDFULL.jpeg',
            "media_type":  "image"
        }
    )

    @gen.coroutine
    def get_more_team_info(self, team_name, params):
        """
        :param team_name: eb|rd|cs|bd
                          eb: enterprise branding; rd: research & development
                          cs: customer success;    bd: business development
        :return: team render data.
        """
        res = yield getattr(self, '_get_{}_info'.format(team_name))(params)
        raise gen.Return(res)

    @gen.coroutine
    def _get_eb_info(self, params):
        data = ObjectDict({})
        user_id, company_id = params.get('user_id'), params.get('company_id')
        conds = {'user_id': user_id, 'company_id': company_id}
        vst_cmpy = yield self.user_company_visit_req_ds.get_visit_cmpy(
            conds=conds, fields=['id', 'company_id'])
        data.relation = ObjectDict({
            'want_visit': self.constant.YES if vst_cmpy else self.constant.NO
        })

        data.header = ObjectDict({
            'type':        'team',
            'name':        '雇主品牌团队',
            'description': '专注于提供企业雇主品牌的策略咨询及实施服务',
            'icon':        '',
            'banner':      'https://cdn.moseeker.com/upload/company_profile/qx'
                           '/banner_qx.jpeg',
        })

        data.templates = [
            ObjectDict({
                'type': 1,
                'sub_type': 'full',
                'title': '团队介绍',
                'data': [{
                    'title':       '',
                    'longtext':    '帮助客户做好雇主品牌'
                                   '的“营销”，通过创意设计和技术实现来优化招聘沟通渠道的内容和目标人群的体验，'
                                   '从而高效传播企业核心价值并提升企业雇主品牌形象，助力企业吸引和保留目标优秀人才。',
                    'media_url':   'https://cdn.moseeker.com/upload/company_profile/qx/'
                                   'EBFULL.jpeg',
                    'media_type':  'image',
                    'member_list': [
                        {
                            "icon":        'https://cdn.moseeker.com/upload/company_profile'
                                           '/qx/neo.jpeg',
                            "name":        'Neo',
                            "title":       '设计师',
                            "description": '我是一个乐观开朗、正气十足的非典型设计师，喜欢篮球，'
                                           '喜欢美食，喜欢奇怪小创意。',
                        },
                        {
                            "icon":        'https://cdn.moseeker.com/upload/company_profile'
                                           '/qx/sheena.jpeg',
                            "name":        'Sheena',
                            "title":       '客户主任',
                            "description": '客户的贴心小棉袄，为客户提供最暖心的支持。同事的知心小姐妹，'
                                           '为同事们排忧解难雪中送碳。',
                        },
                        {
                            "icon":        'https://cdn.moseeker.com/upload/company_profile'
                                           '/qx/dd.jpeg',
                            "name":        '丹丹',
                            "title":       '文案',
                            "description": '略矮略胖，爱写爱吃爱拍爱跑，追星追热点。是一个即使被甲方蹂躏'
                                           '却还一直爱着甲方的文案。',
                        },
                    ]
                }],
            }),

            ObjectDict({
                'type': 1,
                'sub_type': 'less',
                'title': '成员采访',
                'data': [
                    {
                        'title': 'Neo',
                        'longtext': '设计师\n',
                        'media_url': '//v.qq.com/iframe/player.html?vid=x03406mbc69&tiny=0&auto=0',
                        'media_type': 'video',
                        'member_list': []
                    },
                    {
                        'title': 'Sheena',
                        'longtext': '客户主任\n',
                        'media_url': '//v.qq.com/iframe/player.html?vid=k03409eo8so&tiny=0&auto=0',
                        'media_type': 'video',
                        'member_list': []
                    },
                    {
                        'title': '丹丹',
                        'longtext': '文案\n',
                        'media_url': '//v.qq.com/iframe/player.html?vid=b0340sm18mt&tiny=0&auto=0',
                        'media_type': 'video',
                        'member_list': []
                    },
                ],
            }),
            ObjectDict({
                'type':  3,
                'title': "团队在招职位",
                'data':  [{
                        "title":    '文案',
                        "link":
                                    'https://platform.moseeker.com/m/position/131454?wechat_signature=NjYyM2M4ZDAzOTk5NThmNjlhMGI0OWM2ZTgwOTk1Njc2MTU0Y2ZhOQ==',
                        "location": '上海',
                        "salary":   '5k-8k'
                    }]
            })
        ]

        if data.relation.want_visit == 0:
            data.templates.append(ObjectDict({'type': 5, 'title': '', 'data': None}))

        # 其他团队
        otherteam =  ObjectDict({
            'type':     4,
            'sub_type':  0,
            'title':    '其他团队',
            'data':     []
        })
        otherteam.data.append(self._OTHER_TEAM.cs)
        otherteam.data.append(self._OTHER_TEAM.bd)
        otherteam.data.append(self._OTHER_TEAM.rd)
        data.templates.append(otherteam)

        data.templates_total = len(data.templates)

        raise gen.Return(data)

    @gen.coroutine
    def _get_rd_info(self, params):
        data = ObjectDict({})
        user_id, company_id = params.get('user_id'), params.get('company_id')
        conds = {'user_id': user_id, 'company_id': company_id}
        vst_cmpy = yield self.user_company_visit_req_ds.get_visit_cmpy(
            conds=conds, fields=['id', 'company_id'])
        data.relation = ObjectDict({
            'want_visit': self.constant.YES if vst_cmpy else self.constant.NO
        })
        data.header = ObjectDict({
            'type': 'team',
            'name': '研发团队',
            'description': '仟寻招聘的技术保证和动力引擎',
            'icon': '',
            'banner': 'https://cdn.moseeker.com/upload/company_profile/qx'
                      '/banner_qx.jpeg',
        })
        data.templates = [
            ObjectDict({
                'type': 1,
                'sub_type': 'full',
                'title': '团队介绍',
                'data': [{
                    'title':       '研发团队',
                    'longtext':    '我们根据产品需求，不断迭代发布新版本；我们设计开'
                                   '发算法，帮助雇主更快更精准的找到求职者，也帮助求职者找到更心仪的工作。我们通过挖掘大数据，'
                                   '分析候选人关系和行为。我们不断创新技术架构，提高服务稳定性，分享不同知识点，提高研发实力，'
                                   '助力打造一款更具竞争力的产品。',
                    'media_url':   'https://cdn.moseeker.com/upload/company_profile/qx/'
                                   'RDFULL.jpeg',
                    'media_type':  'image',
                    'member_list': [
                        {
                            "icon":        'https://cdn.moseeker.com/upload/company_profile'
                                           '/qx/jianlong.jpeg',
                            "name":        'Jerome',
                            "title":       '开发工程师',
                            "description": '住过加拿大、日本、中国。下班后我和女儿玩过家家。'
                                           '身为一个外国人丝毫没有感受到文化差异。',
                        },
                        {
                            "icon":        'https://cdn.moseeker.com/upload/company_profile'
                                           '/qx/yiliang.jpeg',
                            "name":        '汤亦亮',
                            "title":       '开发工程师',
                            "description": '手艺人，文科好的理科生。虽然经常和同事们“吵架”，但不影响'
                                           '大家的感情，只会让我们更热爱工作。',
                        },
                        {
                            "icon":        'https://cdn.moseeker.com/upload/company_profile'
                                           '/qx/yixin.jpeg',
                            "name":        '潘煜昕',
                            "title":       '技术经理',
                            "description": '行胜于言，希望用技术的力量来提高用户的生活品质。'
                                           '希望打造一款更具竞争力的作品。',
                        },
                    ]
                }],
            }),
            ObjectDict({
                'type': 1,
                'sub_type': 'less',
                'title': '成员采访',
                'data': [
                    {
                        'title': 'Jerome',
                        'longtext': '开发工程师\n',
                        'media_url': '//v.qq.com/iframe/player.html?vid=n03403gqycy&tiny=0&auto=0',
                        'media_type': 'video',
                        'member_list': []
                    },
                    {
                        'title': '亦亮',
                        'longtext': '开发工程师\n',
                        'media_url': '//v.qq.com/iframe/player.html?vid=a03400x38uu&tiny=0&auto=0',
                        'media_type': 'video',
                        'member_list': []
                    },
                    {
                        'title': '煜昕',
                        'longtext': '技术经理\n',
                        'media_url': '//v.qq.com/iframe/player.html?vid=e0340strm66&tiny=0&auto=0',
                        'media_type': 'video',
                        'member_list': []
                    },
                ],
            }),
            ObjectDict({
                'type':  3,
                'title': "团队在招职位",
                'data':  [
                    {
                        "title":    '高级Java软件工程师',
                        "link":
                                    'https://platform.moseeker.com/m/position/131459?wechat_signature=NjYyM2M4ZDAzOTk5NThmNjlhMGI0OWM2ZTgwOTk1Njc2MTU0Y2ZhOQ==',
                        "location": '上海',
                        "salary":   '15k-20k'
                    },
                    {
                        "title":    'web前端开发工程师',
                        "link":
                                    'https://platform.moseeker.com/m/position/131457?wechat_signature=NjYyM2M4ZDAzOTk5NThmNjlhMGI0OWM2ZTgwOTk1Njc2MTU0Y2ZhOQ==',
                        "location": '上海',
                        "salary":   '10k-20k'
                    }
                ]
            })
        ]

        if data.relation.want_visit == 0:
            data.templates.append(ObjectDict({'type': 5, 'title': '', 'data': None}))

        otherteam = ObjectDict({
            'type':     4,
            'sub_type': 0,
            'title':    '其他团队',
            'data':     []
        })
        otherteam.data.append(self._OTHER_TEAM.cs)
        otherteam.data.append(self._OTHER_TEAM.bd)
        otherteam.data.append(self._OTHER_TEAM.eb)
        data.templates.append(otherteam)

        data.templates_total = len(data.templates)

        raise gen.Return(data)

    @gen.coroutine
    def _get_cs_info(self, params):
        data = ObjectDict({})
        user_id, company_id = params.get('user_id'), params.get('company_id')
        conds = {'user_id': user_id, 'company_id': company_id}
        vst_cmpy = yield self.user_company_visit_req_ds.get_visit_cmpy(
            conds=conds, fields=['id', 'company_id'])
        data.relation = ObjectDict({
            'want_visit': self.constant.YES if vst_cmpy else self.constant.NO
        })

        data.header = ObjectDict({
            'type': 'team',
            'name': '客户成功团队',
            'description': '客户的智慧库以及咨询师',
            'icon': '',
            'banner': 'https://cdn.moseeker.com/upload/company_profile/qx'
                      '/banner_qx.jpeg',
        })
        data.templates = [
            ObjectDict({
                'type': 1,
                'sub_type': 'full',
                'title': '团队介绍',
                'data': [{
                    'title':       '客户成功团队',
                    'longtext':    '我们团队主要工作是，提供运营策略给到我们的客户，并提供运营技术支持，'
                                   '是成单后客户的智慧库以及咨询师。',
                    'media_url':   'https://cdn.moseeker.com/upload/company_profile/qx/'
                                   'CSFULL.png',
                    'media_type':  'image',
                    'member_list': [
                        {
                            "icon":        'https://cdn.moseeker.com/upload/company_profile'
                                           '/qx/feixia.jpeg',
                            "name":        '肖飞霞',
                            "title":       '客户项目顾问',
                            "description": '给客户出谋划策、答疑解难。希望有个不被打扰的假期，'
                                           '希望所有的idea都被客户采纳，希望世界和平！',
                        },
                        {
                            "icon":        'https://cdn.moseeker.com/upload/company_profile'
                                           '/qx/Melissa.jpeg',
                            "name":        'Melissa',
                            "title":       '客户成功团队经理',
                            "description": '热衷于规划与整理，连出去旅游都能整出一个action plan。'
                                           '坚信完美规划流程，可以使工作效率更高。',
                        },
                        {
                            "icon":        'https://cdn.moseeker.com/upload/company_profile'
                                           '/qx/Julie.jpeg',
                            "name":        'Julie',
                            "title":       '客户项目顾问',
                            "description": '也许我正在on-call，也许我只是默默的站在程序猿身边。'
                                           '你若安好，我便晴天，你若灿烂，喜大普奔！ ',
                        },
                    ]
                }],
            }),
            ObjectDict({
                'type': 1,
                'sub_type': 'less',
                'title': '成员采访',
                'data': [
                    {
                        'title': '肖飞霞',
                        'longtext': '客户项目顾问\n',
                        'media_url': '//v.qq.com/iframe/player.html?vid=p034057d7ix&tiny=0&auto=0',
                        'media_type': 'video',
                        'member_list': []
                    },
                    {
                        'title': 'Melissa/Julie',
                        'longtext': '客户成功团队经理/项目顾问\n',
                        'media_url': '//v.qq.com/iframe/player.html?vid=u03404uht6u&tiny=0&auto=0',
                        'media_type': 'video',
                        'member_list': []
                    },
                ],
            }),
            ObjectDict({
                'type': 3,
                'title': "团队在招职位",
                'data': [{
                        "title":    '运营专员',
                        "link":
                                    'https://platform.moseeker.com/m/position/134251?wechat_signature=NjYyM2M4ZDAzOTk5NThmNjlhMGI0OWM2ZTgwOTk1Njc2MTU0Y2ZhOQ==',
                        "location": '上海',
                        "salary":   '3k-6k'
                    }]
            })
        ]
        if data.relation.want_visit == 0:
            data.templates.append(ObjectDict({'type': 5, 'title': '', 'data': None}))

        otherteam = ObjectDict({
            'type':     4,
            'sub_type': 0,
            'title':    '其他团队',
            'data':     []
        })
        otherteam.data.append(self._OTHER_TEAM.rd)
        otherteam.data.append(self._OTHER_TEAM.bd)
        otherteam.data.append(self._OTHER_TEAM.eb)
        data.templates.append(otherteam)

        data.templates_total = len(data.templates)

        raise gen.Return(data)

    @gen.coroutine
    def _get_bd_info(self, params):
        data = ObjectDict({})
        user_id, company_id = params.get('user_id'), params.get('company_id')
        conds = {'user_id': user_id, 'company_id': company_id}
        vst_cmpy = yield self.user_company_visit_req_ds.get_visit_cmpy(
            conds=conds, fields=['id', 'company_id'])
        data.relation = ObjectDict({
            'want_visit': self.constant.YES if vst_cmpy else self.constant.NO
        })

        data.header = ObjectDict({
            'type': 'team',
            'name': '商务拓展团队',
            'description': '开发优秀企业，提供合作方案，解决招聘难题，提升雇主形象',
            'icon': '',
            'banner': 'https://cdn.moseeker.com/upload/company_profile/qx'
                      '/banner_qx.jpeg',
        })
        data.templates = [
            ObjectDict({
                'type': 1,
                'sub_type': 'full',
                'title': '团队介绍',
                'data': [{
                    'title':       '商务拓展团队',
                    'longtext':    '团队成员基本都是狼性十足的小伙子们，业务团队既要有非常有狼性，又要非常重要的责任心和工作能力，去帮助客户搭建一对一的专业服务，我们团队的宗旨是：客户选择我们一定是最正确的选择。',
                    'media_url':   'https://cdn.moseeker.com/upload/company_profile/qx/'
                                   'BDFULL.jpeg',
                    'media_type':  'image',
                    'member_list': [
                        {
                            "icon":        'https://cdn.moseeker.com/upload/company_profile'
                                           '/qx/Austin.jpeg',
                            "name":        'Austin',
                            "title":       '大客户经理',
                            "description": '非典型理科男，热爱挑战和摄影，希望变成一个有故事的有趣男子。'
                                           '最享受同时HOLD住HR轮番提问的时刻。',
                        },
                        {
                            "icon":        'https://cdn.moseeker.com/upload/company_profile'
                                           '/qx/Kayle.jpeg',
                            "name":        'Kayle',
                            "title":       '大客户经理',
                            "description": '名字来源于北欧神话。本人狮子座阳光灿烂，喜欢和客户沟通成功合'
                                           '作那一刻的成就感，喜欢交朋友。',
                        },
                    ]
                }],
            }),
            ObjectDict({
                'type': 1,
                'sub_type': 'less',
                'title': '成员采访',
                'data': [
                    {
                        'title': 'Austin',
                        'longtext': '大客户经理\n',
                        'media_url': '//v.qq.com/iframe/player.html?vid=z0340r5m00d&tiny=0&auto=0',
                        'media_type': 'video',
                        'member_list': []
                    },
                    {
                        'title': 'Kayle',
                        'longtext': '大客户经理\n',
                        'media_url': '//v.qq.com/iframe/player.html?vid=h03408ryvbo&tiny=0&autos=0',
                        'media_type': 'video',
                        'member_list': []
                    },
                ],
            }),
            ObjectDict({
                'type':  3,
                'title': "团队在招职位",
                'data':  [
                    {
                        "title":    '销售顾问',
                        "link":
                                    'https://platform.moseeker.com/m/position/131455?wechat_signature=NjYyM2M4ZDAzOTk5NThmNjlhMGI0OWM2ZTgwOTk1Njc2MTU0Y2ZhOQ==',
                        "location": '北京',
                        "salary":   '5k-10k'
                    },
                    {
                        "title":    '大客户代表',
                        "link":
                                    'https://platform.moseeker.com/m/position/133864?wechat_signature=NjYyM2M4ZDAzOTk5NThmNjlhMGI0OWM2ZTgwOTk1Njc2MTU0Y2ZhOQ==',
                        "location": '北京',
                        "salary":   '5k-10k'
                    }
                ]
            })
        ]
        if data.relation.want_visit == 0:
            data.templates.append(ObjectDict({'type': 5, 'title': '', 'data': None}))

        otherteam = ObjectDict({
            'type':     4,
            'sub_type': 0,
            'title':    '其他团队',
            'data':     []
        })
        otherteam.data.append(self._OTHER_TEAM.cs)
        otherteam.data.append(self._OTHER_TEAM.rd)
        otherteam.data.append(self._OTHER_TEAM.eb)
        data.templates.append(otherteam)

        data.templates_total = len(data.templates)

        raise gen.Return(data)
