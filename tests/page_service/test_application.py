# coding=utf-8

import unittest
import functools
from util.tool.dict_tool import objectdictify
import conf.common as const

class ApplicationPSTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.json_config = [{'fields': [{'company_id':        0,
                                         'create_time':       '2015-11-09 23:11:59',
                                         'disable':           0,
                                         'field_description': '',
                                         'field_name':        'name',
                                         'field_title':       '姓名',
                                         'field_type':        0,
                                         'field_value':       [['']],
                                         'id':                2,
                                         'is_basic':          0,
                                         'map':               'basicinfo.name',
                                         'priority':          2,
                                         'required':          0,
                                         'update_time':       '2015-12-04 08:24:39'},
                                        {'company_id':        0,
                                         'create_time':       '2015-11-09 23:11:59',
                                         'disable':           0,
                                         'field_description': '',
                                         'field_name':        'gender',
                                         'field_title':       '性别',
                                         'field_type':        3,
                                         'field_value':       [
                                             ['男', '1'], ['女', '2']],
                                         'id':                5,
                                         'is_basic':          0,
                                         'map':               'basicinfo.gender',
                                         'priority':          5,
                                         'required':          0,
                                         'update_time':       '2015-12-03 12:48:36'},
                                        {'company_id':        0,
                                         'create_time':       '2015-11-09 23:12:00',
                                         'disable':           0,
                                         'field_description': '',
                                         'field_name':        'idnumber',
                                         'field_title':       '身份证号码',
                                         'field_type':        0,
                                         'field_value':       [['']],
                                         'id':                15,
                                         'is_basic':          0,
                                         'map':               'basicinfo.idnumber',
                                         'priority':          15,
                                         'required':          0,
                                         'update_time':       '2015-11-27 06:33:32'},
                                        {'company_id':        0,
                                         'create_time':       '2015-11-09 23:11:59',
                                         'disable':           0,
                                         'field_description': '',
                                         'field_name':        'mobile',
                                         'field_title':       '手机',
                                         'field_type':        0,
                                         'field_value':       [['']],
                                         'id':                3,
                                         'is_basic':          0,
                                         'map':               'basicinfo.mobile',
                                         'priority':          3,
                                         'required':          0,
                                         'update_time':       '2015-12-04 08:24:39'},
                                        {'company_id':        0,
                                         'create_time':       '2015-11-09 23:11:59',
                                         'disable':           0,
                                         'field_description': '',
                                         'field_name':        'email',
                                         'field_title':       '邮箱',
                                         'field_type':        0,
                                         'field_value':       [['']],
                                         'id':                11,
                                         'is_basic':          0,
                                         'map':               'basicinfo.email',
                                         'priority':          11,
                                         'required':          0,
                                         'update_time':       '2015-11-27 06:33:32'},
                                        {'company_id':        0,
                                         'create_time':       '2015-11-09 23:12:00',
                                         'disable':           0,
                                         'field_description': '',
                                         'field_name':        'location',
                                         'field_title':       '现居住地',
                                         'field_type':        0,
                                         'field_value':       [['']],
                                         'id':                16,
                                         'is_basic':          0,
                                         'map':               'basicinfo.location',
                                         'priority':          16,
                                         'required':          0,
                                         'update_time':       '2015-11-27 06:33:32'},
                                        {'company_id':        0,
                                         'create_time':       '2016-04-18 16:06:42',
                                         'disable':           0,
                                         'field_description': '',
                                         'field_name':        'Address',
                                         'field_title':       '通讯地址',
                                         'field_type':        0,
                                         'field_value':       [['']],
                                         'id':                61,
                                         'is_basic':          0,
                                         'map':               '',
                                         'priority':          61,
                                         'required':          0,
                                         'update_time':       '2016-11-24 10:03:01'}],
                             'title':  '基本信息'},
                            {'fields':      [{'company_id':        0,
                                              'create_time':       '2015-11-09 23:12:00',
                                              'disable':           0,
                                              'field_description': '',
                                              'field_name':        'degree',
                                              'field_title':       '学历',
                                              'field_type':        10,
                                              'field_value':       [
                                                  ['大专以下', '1'],
                                                  ['大专', '2'],
                                                  ['本科', '3'],
                                                  ['硕士', '4'],
                                                  ['博士', '5'],
                                                  ['博士以上', '6']],
                                              'id':                17,
                                              'is_basic':          0,
                                              'map':               'basicinfo.degree',
                                              'priority':          17,
                                              'required':          0,
                                              'update_time':       '2016-04-27 13:56:18'},
                                             {'company_id':        0,
                                              'create_time':       '2015-11-09 23:12:00',
                                              'disable':           0,
                                              'field_description': '',
                                              'field_name':        'graduation',
                                              'field_title':       '预计毕业时间',
                                              'field_type':        6,
                                              'field_value':       [
                                                  ['']],
                                              'id':                19,
                                              'is_basic':          1,
                                              'map':               'score.graduation',
                                              'priority':          19,
                                              'required':          0,
                                              'update_time':       '2015-11-27 06:33:32'},
                                             {'company_id':        0,
                                              'create_time':       '2015-11-09 23:12:00',
                                              'disable':           0,
                                              'field_description': '',
                                              'field_name':        'education',
                                              'field_title':       '教育经历',
                                              'field_type':        9,
                                              'field_value':       [
                                                  ['']],
                                              'id':                18,
                                              'is_basic':          0,
                                              'map':               'education',
                                              'priority':          18,
                                              'required':          0,
                                              'update_time':       '2015-11-27 06:33:32'},
                                             {'company_id':        0,
                                              'create_time':       '2015-11-09 23:12:00',
                                              'disable':           0,
                                              'field_description': '',
                                              'field_name':        'gpa',
                                              'field_title':       'GPA',
                                              'field_type':        11,
                                              'field_value':       [
                                                  ['']],
                                              'id':                28,
                                              'is_basic':          1,
                                              'map':               'score.gpa',
                                              'priority':          28,
                                              'required':          0,
                                              'update_time':       '2015-12-04 07:28:39'},
                                             {'company_id':        0,
                                              'create_time':       '2015-11-09 23:12:00',
                                              'disable':           0,
                                              'field_description': '',
                                              'field_name':        'cet4',
                                              'field_title':       '四级成绩',
                                              'field_type':        11,
                                              'field_value':       [
                                                  ['']],
                                              'id':                22,
                                              'is_basic':          1,
                                              'map':               'score.cet4',
                                              'priority':          22,
                                              'required':          0,
                                              'update_time':       '2015-12-04 07:28:39'},
                                             {'company_id':        0,
                                              'create_time':       '2015-11-09 23:12:00',
                                              'disable':           0,
                                              'field_description': '',
                                              'field_name':        'cet6',
                                              'field_title':       '六级成绩',
                                              'field_type':        11,
                                              'field_value':       [
                                                  ['']],
                                              'id':                23,
                                              'is_basic':          1,
                                              'map':               'score.cet6',
                                              'priority':          23,
                                              'required':          0,
                                              'update_time':       '2015-12-04 07:28:39'}],
                             'placeholder': '第2步',
                             'title':       '第2步'},
                            {'fields':      [{'company_id':        0,
                                              'create_time':       '2015-11-09 23:12:01',
                                              'disable':           0,
                                              'field_description': '',
                                              'field_name':        'internship',
                                              'field_title':       '实习经历',
                                              'field_type':        9,
                                              'field_value':       [
                                                  ['']],
                                              'id':                35,
                                              'is_basic':          1,
                                              'map':               'workexperience.internship',
                                              'priority':          34,
                                              'required':          0,
                                              'update_time':       '2015-11-30 05:29:10'},
                                             {'company_id':        0,
                                              'create_time':       '2015-11-09 23:12:00',
                                              'disable':           0,
                                              'field_description': '',
                                              'field_name':        'schooljob',
                                              'field_title':       '校内职务',
                                              'field_type':        9,
                                              'field_value':       [
                                                  ['']],
                                              'id':                31,
                                              'is_basic':          1,
                                              'map':               'score.schooljob',
                                              'priority':          31,
                                              'required':          0,
                                              'update_time':       '2015-11-27 06:33:33'},
                                             {'company_id':        0,
                                              'create_time':       '2015-11-09 23:12:00',
                                              'disable':           0,
                                              'field_description': '',
                                              'field_name':        'competition',
                                              'field_title':       '获得奖项',
                                              'field_type':        4,
                                              'field_value':       [
                                                  ['']],
                                              'id':                29,
                                              'is_basic':          1,
                                              'map':               'score.competition',
                                              'priority':          29,
                                              'required':          0,
                                              'update_time':       '2016-04-25 10:58:54'}],
                             'placeholder': '第3步',
                             'title':       '第3步'},
                            {'fields':      [{'company_id':        0,
                                              'create_time':       '2015-11-09 23:12:01',
                                              'disable':           0,
                                              'field_description': '输入您对自己的简短评价。请简明扼要的说明您最大的优势是什么',
                                              'field_name':        'remarks',
                                              'field_title':       '自我介绍',
                                              'field_type':        1,
                                              'field_value':       [
                                                  ['']],
                                              'id':                45,
                                              'is_basic':          0,
                                              'map':               'remarks',
                                              'priority':          45,
                                              'required':          0,
                                              'update_time':       '2015-11-27 06:33:34'},
                                             {'company_id':        0,
                                              'create_time':       '2015-11-09 23:12:01',
                                              'disable':           0,
                                              'field_description': '',
                                              'field_name':        'expectsalary',
                                              'field_title':       '期望年薪',
                                              'field_type':        10,
                                              'field_value':       [
                                                  ['6万以下', '1'],
                                                  ['6万-8万', '2'],
                                                  ['8万-12万', '3'],
                                                  ['12-20万', '4'],
                                                  ['20万-30万', '5'],
                                                  ['30万以上', '6']],
                                              'id':                39,
                                              'is_basic':          0,
                                              'map':               'intention.expectsalary',
                                              'priority':          39,
                                              'required':          0,
                                              'update_time':       '2016-04-28 20:56:20'},
                                             {'company_id':        0,
                                              'create_time':       '2015-11-09 23:12:01',
                                              'disable':           0,
                                              'field_description': '',
                                              'field_name':        'trip',
                                              'field_title':       '是否接受长期出差',
                                              'field_type':        3,
                                              'field_value':       [
                                                  ['接受', '1'],
                                                  ['不接受', '2']],
                                              'id':                43,
                                              'is_basic':          0,
                                              'map':               'intention.trip',
                                              'priority':          43,
                                              'required':          1,
                                              'update_time':       '2016-05-03 11:44:29'}],
                             'placeholder': '第4步',
                             'title':       '第4步'}]

        self.field_value = '[{"fields":[{"field_description":"","company_id":0,"create_time":"2015-11-09 23:11:59","priority":2,"field_title":"姓名","required":0,"is_basic":0,"field_name":"name","update_time":"2015-12-04 08:24:39","disable":0,"field_value":[[""]],"id":2,"field_type":0,"map":"basicinfo.name"},{"field_description":"","company_id":0,"create_time":"2015-11-09 23:11:59","priority":3,"field_title":"手机","required":0,"is_basic":0,"field_name":"mobile","update_time":"2015-12-04 08:24:39","disable":0,"field_value":[[""]],"id":3,"field_type":0,"map":"basicinfo.mobile"},{"field_description":"","company_id":0,"create_time":"2015-11-09 23:12:00","priority":18,"field_title":"教育经历","required":0,"is_basic":0,"field_name":"education","update_time":"2015-11-27 06:33:32","disable":0,"field_value":[[""]],"id":18,"field_type":9,"map":"education"},{"field_description":"","company_id":0,"create_time":"2015-11-09 23:12:00","priority":33,"field_title":"工作经历","required":0,"is_basic":0,"field_name":"workexp","update_time":"2015-11-27 06:33:33","disable":0,"field_value":[[""]],"id":33,"field_type":9,"map":"workexp"},{"field_description":"","company_id":0,"create_time":"2015-11-09 23:12:00","priority":34,"field_title":"项目经历","required":0,"is_basic":0,"field_name":"projectexp","update_time":"2015-11-27 06:33:34","disable":0,"field_value":[[""]],"id":34,"field_type":9,"map":"projectexp"}],"title":"基本信息"}]'

    def test_make_fields_to_check(self):
        def _merge(x, y):
            x.extend(y)
            return x

        json_config = objectdictify(self.json_config)
        fields = functools.reduce(_merge, [page.fields for page in json_config])
        fileds_to_check = [f for f in objectdictify(fields) if f.required == const.OLD_YES]
        field_names = [f.field_name for f in fileds_to_check]
        self.assertIn('gpa', field_names)
        self.assertIn('idnumber', field_names)
        self.assertIn('Address', field_names)
    #
    # def test_filed_value(self):
    #     pprint.pprint(json_decode(self.field_value))


if __name__ == "__main__":
    unittest.main()
