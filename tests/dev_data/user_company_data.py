# # -*- coding=utf-8 -*-
# # Copyright 2016 MoSeeker
#
# """
# :author 马超（machao@moseeker.com）
# :date 2016.10.12
#
# 已废弃 by 煜昕 2017.5.25
#
# """
# from util.common import ObjectDict
# from util.tool.url_tool import make_url
# import conf.path as path
#
#
# def _add_company_data(hander_params, data):
#     """构建公司主页的豆腐干们"""
#
#     data.templates = [
#         ObjectDict({
#             'type': 1,
#             'sub_type': 'less',
#             'title': '办公环境',
#             'data': WORKING_ENV,
#             'more_link': ''
#         }),
#         ObjectDict({'type': 2, 'title': 'template 2', 'data': data2}),
#         ObjectDict({
#             'type': 1,
#             'sub_type': 'less',
#             'title': '我们的团队',
#             'data': TEAMS,
#             'more_link': make_url(path.COMPANY_TEAM, hander_params)
#         }),
#         ObjectDict({
#             'type': 1,
#             'sub_type': 'less',
#             'title': '在这里工作的人们',
#             'data': MEMBERS,
#             'more_link': ''
#         }),
#         ObjectDict({
#             'type': 4,
#             'sub_type': 0,
#             'title': '公司大事件',
#             'data': data4_1
#         }),
#         # 可能感兴趣的公司，暂时不做
#         # ObjectDict({'type': 4, 'sub_type': 1, 'title': '你可能感兴趣的公司',
#         #             'data': data4_2}),
#         ObjectDict({'type': 50, 'title': 'address', 'data': data50}),
#         ObjectDict({'type': 5, 'title': '', 'data': None})
#     ]
#     data.template_total = len(data.templates)
#
#
#
# def _add_team_data(hander_params, data):
#     """构建团队主页的豆腐干们"""
#
#     data.templates = [
#         ObjectDict({
#             'type': 1,
#             'sub_type': 'middle',
#             'title': '研发团队',
#             'data': TEAM_RD,
#             'more_link': make_url('/m/company/team/rd', hander_params)
#         }),
#
#         ObjectDict({
#             'type': 1,
#             'sub_type': 'middle',
#             'title': '客户成功团队',
#             'data': TEAM_CS,
#             'more_link': make_url('/m/company/team/cs', hander_params)
#         }),
#
#         ObjectDict({
#             'type': 1,
#             'sub_type': 'middle',
#             'title': '商务拓展团队',
#             'data': TEAM_BD,
#             'more_link': make_url('/m/company/team/bd', hander_params)
#         }),
#
#         ObjectDict({
#             'type': 1,
#             'sub_type': 'middle',
#             'title': '雇主品牌团队',
#             'data': TEAM_EB,
#             'more_link': make_url('/m/company/team/eb', hander_params)
#         }),
#     ]
#     data.template_total = len(data.templates)
#
#
#
#
#
# WORKING_ENV = [
#     {
#         'title': "EB, CS, BD办公区域",
#         'longtext': "",
#         'media_url': 'https://cdn.moseeker.com/upload/company_profile/qx/e1.jpeg',
#         'media_type': 'image',
#         'member_list': []
#     },
#     {
#         'title': "一楼大会议室",
#         'longtext': "",
#         'media_url': 'https://cdn.moseeker.com/upload/company_profile/qx/meetingroom.jpeg',
#         'media_type': 'image',
#         'member_list': []
#     },
#     {
#         'title': "EB, CS, BD办公区域",
#         'longtext': "",
#         'media_url': 'https://cdn.moseeker.com/upload/company_profile/qx/e2.jpeg',
#         'media_type': 'image',
#         'member_list': []
#     },
#     {
#         'title': "数据、研发、技术团队办公区域",
#         'longtext': "",
#         'media_url': 'https://cdn.moseeker.com/upload/company_profile/qx/t1.jpeg',
#         'media_type': 'image',
#         'member_list': []
#     },
#     {
#         'title': "楼梯走廊装饰壁画",
#         'longtext': "",
#         'media_url': 'https://cdn.moseeker.com/upload/company_profile/qx/stair.jpeg',
#         'media_type': 'image',
#         'member_list': []
#     },
#     {
#         'title': "EB, CS, BD办公区域",
#         'longtext': "",
#         'media_url': 'https://cdn.moseeker.com/upload/company_profile/qx/e3.jpeg',
#         'media_type': 'image',
#         'member_list': []
#     }
# ]
#
# TEAMS = [
#     {
#         'title': "客户成功团队",
#         'longtext': "提供运营策略给到客户，并提供技术支持，是成单后客户的智慧库以及咨询师。"
#                     "需要细心的执行外，还要根据各客户实际情况提供相应的策略。",
#         'media_url': 'https://cdn.moseeker.com/upload/company_profile/qx/cs.png',
#         'media_type': 'image',
#         'member_list': []
#     },
#     {
#         'title': "研发团队",
#         'longtext': "提供技术保证和动力引擎。我们不断创新技术架构，提高服务稳定性，"
#                     "分享不同知识点，提高研发实力，助力打造一款更具竞争力的产品。",
#         'media_url': 'https://cdn.moseeker.com/upload/company_profile/qx/rd.jpeg',
#         'media_type': 'image',
#         'member_list': []
#     },
#     {
#         'title': "雇主品牌团队",
#         'longtext': "专注于提供企业雇主品牌的策略咨询及实施服务。通过创意设计和技术实现来"
#                     "优化招聘渠道和目标人群的体验，助力吸引和保留目标优秀人才。",
#         'media_url': 'https://cdn.moseeker.com/upload/company_profile/qx/eb.jpeg',
#         'media_type': 'image',
#         'member_list': []
#     },
#     {
#         'title': "商务拓展团队",
#         'longtext': "提供给客户在移动社交招聘、雇主品牌建设上的合作方案，解决企业招聘难题，"
#                     "提升雇主品牌形象。客户选择我们一定是最正确的选择。",
#         'media_url': 'https://cdn.moseeker.com/upload/company_profile/qx/bd.jpeg',
#         'media_type': 'image',
#         'member_list': []
#     }
# ]
#
# data1 = [
#     {
#         'title': "xsss",
#         'longtext': "完美主义 BELLA。设计是一切的开始，我们非常注重细节和整体的把握。",
#         'media_url': '//v.qq.com/iframe/player.html?vid=b0338mt86yc&tiny=0&auto=0',
#         'media_type': 'video',
#         'member_list': []
#     },
#     {
#         'title': "我的团队",
#         'longtext': "完美主义 BELLA。设计是一切的开始，我们非常注重细节和整体的把握，旨在给用户一种优雅旨在给用户高效的体验。完美主义 BELLA。设计是一切的开始，我们非常注重细节和整体的把握。",
#         'media_url': 'http://o8g4x4uja.bkt.clouddn.com/15008518202_c265dfa55f_h.jpg',
#         'media_type': 'image',
#         'member_list': []
#     }
# ]
#
# data2 = [
#     {
#         'title': '王向导',
#         'description': '两年前，我成立了 MoSeeker。我的梦想是，将 MoSeeker 打造成全球顶尖的优秀企业，帮每个人找到喜欢的工作。',
#         'media_url': 'http://o8g4x4uja.bkt.clouddn.com/We_Chat_1467010816.png',
#         'media_type': 'image'
#     }
# ]
#
# MEMBERS = [
#     {
#         'title': "潘煜昕",
#         'longtext': "技术经理\n"
#                     "行胜于言，希望用技术的力量来提高用户的生活品质。"
#                     "我们不断创新技术架构，助力打造一款更具竞争力的产品。",
#         'media_url': '//v.qq.com/iframe/player.html?vid=e0340strm66&tiny=0&auto=0',
#         'media_type': 'video',
#         'member_list': []
#     },
#     {
#         'title': "Melissa & Julie",
#         'longtext': "客户成功团队成员\n"
#                     "热衷于规划与整理，连出去旅游都能整出一个action plan。"
#                     "坚信流程上的well organized，可以使工作more efficient。",
#         'media_url': '//v.qq.com/iframe/player.html?vid=u03404uht6u&tiny=0&auto=0',
#         'media_type': 'video',
#         'member_list': []
#     },
#     {
#         'title': "Kayle",
#         'longtext': "大客户经理\n"
#                     "名字来源于北欧神话里的大天使长，本人狮子座阳光灿烂，"
#                     "喜欢和客户沟通成功合作那一刻的成就感，喜欢交朋友。",
#         'media_url': '//v.qq.com/iframe/player.html?vid=h03408ryvbo&tiny=0&auto=0',
#         'media_type': 'video',
#         'member_list': []
#     }
# ]
#
# data3 = [
#     {
#         'title':    '招设计师',
#         'link':     'https://www.moseeker.com',
#         'location': '上海, 北京, 广州',
#         'salary':   '12k - 15k'
#     },
#     {
#         'title':    '招设计师',
#         'link':     'http://www.baidu.com',
#         'location': '上海',
#         'salary':   '12k以上'
#     }
# ]
#
# data4_1 = [
#     {
#         'title': '2015年',
#         'description': '获得由国内顶尖人力资源权威媒体《人力资本管理》颁发的2014-2015大中华区人力资源服务创新大奖',
#         'media_url': 'https://cdn.moseeker.com/upload/company_profile/qx/ds3.jpeg',
#         'media_type': 'image',
#     },
#     {
#         'title': '2016年9月14日',
#         'description': '获选“2016-红鲱鱼亚洲100 强”最具潜力创业公司。',
#         'media_url': 'https://cdn.moseeker.com/upload/company_profile/qx/ds2.jpeg',
#         'media_type': 'image',
#     },
#     {
#         'title': '2016年10月',
#         'description': '仟寻招聘跻身中国创新创业大赛8强，获得国赛优秀企业称号。',
#         'media_url': 'https://cdn.moseeker.com/upload/company_profile/qx/ds1.jpeg',
#         'media_type': 'image',
#     }
# ]
#
# data4_2 = [
#     {
#         'title': 'Airbnb',
#         'media_url': 'http://o8g4x4uja.bkt.clouddn.com/medium_logo.png',
#         'link': 'string'
#     },
#     {
#         'title': 'Airbnb',
#         'media_url': 'http://o8g4x4uja.bkt.clouddn.com/medium_logo.png',
#         'link': 'string'
#     },
#     {
#         'title': 'Airbnb',
#         'media_url': 'http://o8g4x4uja.bkt.clouddn.com/medium_logo.png',
#         'link': 'string'
#     }
# ]
#
#
# data50 = [
#     {
#         'lat': '31.196240',
#         'lng': '121.432440',
#         'location_detail': "徐汇区乐山路 33 号慧谷创业一号楼 708 室"
#     }
# ]
#
# TEAM_RD = [{
#     'title':       "研发团队",
#     'longtext':    "我们根据产品需求，不断迭代发布新版本；"
#                    "我们设计开发算法，帮助雇主更快更精准的找到求职者，也帮助求职者找到更心仪的工作。"
#                    "我们通过挖掘大数据，分析候选人关系和行为。"
#                    "我们不断创新技术架构，提高服务稳定性，分享不同知识点，提高研发实力，助力打造一款更具竞争力的产品。",
#     'media_url':   'https://cdn.moseeker.com/upload/company_profile/qx/rd.jpeg',
#     'media_type':  'image',
#     'member_list': [
#         {
#             "icon":        'https://cdn.moseeker.com/upload/company_profile'
#                            '/qx/jianlong.jpeg',
#             "name":        'Jerome Beaulieu',
#             "title":       '开发工程师',
#             "description": '地球民 住过在加拿大，日本，中国。我是工程师，说得具体我整天按键。'
#                            '下班后我和女儿玩过家家。',
#         },
#         {
#             "icon":        'https://cdn.moseeker.com/upload/company_profile'
#                            '/qx/yiliang.jpeg',
#             "name":        '汤亦亮',
#             "title":       '开发工程师',
#             "description": '手艺人，文科好的理科生',
#         },
#         {
#             "icon":        'https://cdn.moseeker.com/upload/company_profile'
#                            '/qx/yixin.jpeg',
#             "name":        '潘煜昕',
#             "title":       '技术经理',
#             "description": '行胜于言，希望用技术的力量来提高用户的生活品质。',
#         },
#
#     ]
# }]
#
# TEAM_CS = [{
#     'title':       "客户成功团队",
#     'longtext':    "我们团队都是年轻貌美的姑娘们。由于工作的内容需要细心的执行外，还要根据各客户的实际情况提供相应的策略，我们的团队成员都是智慧与貌美并重。",
#     'media_url':   'https://cdn.moseeker.com/upload/company_profile/qx/cs.png',
#     'media_type':  'image',
#     'member_list': [
#         {
#             "icon":        'https://cdn.moseeker.com/upload/company_profile'
#                            '/qx/feixia.jpeg',
#             "name":        '肖飞霞',
#             "title":       'CS',
#             "description": '人生三件大事，吃饭，睡觉，给客户出谋划策、答疑解难。三大希望，希望'
#                            '有个不被打扰的假期，希望所有的idea都被客户采纳，希望世界和平！',
#         },
#         {
#             "icon":        'https://cdn.moseeker.com/upload/company_profile'
#                            '/qx/Melissa.jpeg',
#             "name":        'Melissa',
#             "title":       'Head of Customer Success',
#             "description": '热衷于规划与整理，连出去旅游都能整出一个action plan。坚信流程上的'
#                            'well organized，可以使工作more efficient。',
#         },
#         {
#             "icon":        'https://cdn.moseeker.com/upload/company_profile'
#                            '/qx/Julie.jpeg',
#             "name":        'Julie',
#             "title":       'CS',
#             "description": '不要问我在干嘛，也许我正在con-call，也许我正在与excel、'
#                            'ppt大战，也许我只是默默的站在程序员哥哥身边，你懂的。。。'
#                            '总而言之，你若安好，我便晴天，你若灿烂，喜大普奔！我的愿望是，'
#                            'Be nice ：）',
#         },
#
#     ]
# }]
#
# TEAM_BD = [{
#     'title':       "商务拓展团队",
#     'longtext':    "我们团队主要工作是开发各行业的优秀企业，提供给客户在移动社交招聘、"
#                    "雇主品牌建设上的合作方案，从而解决企业招聘难题，提升雇主形象。",
#     'media_url':   'https://cdn.moseeker.com/upload/company_profile/qx/bd.jpeg',
#     'media_type':  'image',
#     'member_list': [
#         {
#             "icon":        'https://cdn.moseeker.com/upload/company_profile/qx/Austin.jpeg',
#             "name":        'Austin',
#             "title":       '大客户经理',
#             "description": '非典型理科男，热爱挑战和摄影，希望变成一个有故事的有趣男子。'
#                            '喜欢亲自去看看不同行业的公司风格, '
#                            '最享受同时HOLD住HR轮番提问的时刻，欧耶~',
#         },
#         {
#             "icon":        'https://cdn.moseeker.com/upload/company_profile/qx/Kayle.jpeg',
#             "name":        'Kayle',
#             "title":       '大客户经理',
#             "description": '名字来源于北欧神话里的大天使长，本人狮子座阳光灿烂（呸），'
#                            '喜欢和客户沟通成功合作那一刻的成就感，喜欢交朋友。',
#         },
#     ]
# }]
#
# TEAM_EB = [{
#     'title':       "雇主品牌团队",
#     'longtext':    "雇主品牌团队专注于提供企业雇主品牌的策略咨询及实施服务。帮助客户做好雇主品牌的“营销”，通过创意设计和技术实现来优化招聘沟通渠道的内容和目标人群的体验，从而高效传播企业核心价值并提升企业雇主品牌形象，助力企业吸引和保留目标优秀人才",
#     'media_url':   'https://cdn.moseeker.com/upload/company_profile/qx/EBFULL.jpeg',
#     'media_type':  'image',
#     'member_list': [
#         {
#             "icon":        'https://cdn.moseeker.com/upload/company_profile/qx/neo.jpeg',
#             "name":        'Neo',
#             "title":       '设计师',
#             "description": '乐观开朗正气十足的非典型设计师 喜欢奇怪小创意。',
#         },
#         {
#             "icon":        'https://cdn.moseeker.com/upload/company_profile/qx/sheena.jpeg',
#             "name":        'Sheena',
#             "title":       '客户主任',
#             "description": '客户的贴心小棉袄，同事的知心小姐妹。一门心思期待在雇主品牌领域能够为客户提供更杰出的服务！',
#         },
#         {
#             "icon":        'https://cdn.moseeker.com/upload/company_profile/qx/dd.jpeg',
#             "name":        '丹丹',
#             "title":       '文案',
#             "description": '略矮略胖，爱写爱吃爱拍爱跑，追星追热点。希望成为一个即使被蹂躏却还是一如既往爱着客户的文案，说的想哭！',
#         },
#     ]
# }]
