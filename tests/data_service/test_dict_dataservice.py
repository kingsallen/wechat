# coding=utf-8

from tornado.testing import AsyncTestCase, gen_test, main
from service.data.infra.thrift_dict import DictDataService
from pprint import pprint


class DictDataServiceTestCase(AsyncTestCase):
    """测试前,保证基础服务稳定可用
    """

    @gen_test
    def test_industry_fetch(self):
        service = DictDataService()
        i = yield service.get_industries()
        pprint(i)
        self.assertIsInstance(i, list)

    @gen_test
    def test_function_fetch_l1(self):
        service = DictDataService()
        f1 = yield service.get_function()
        pprint(f1)
        self.assertIsInstance(f1, list)

    @gen_test
    def test_function_fetch_l2(self):
        service = DictDataService()
        f2 = yield service.get_function(code=200000)
        pprint(f2)
        self.assertIsInstance(f2, list)

    @gen_test
    def test_city_fetch(self):
        service = DictDataService()
        c = yield service.get_cities()
        pprint(c)
        self.assertIsInstance(c, list)

    @gen_test
    def test_hot_city_fetch(self):
        service = DictDataService()
        c = yield service.get_hot_cities()
        pprint(c)
        self.assertIsInstance(c, list)

    @gen_test
    def test_get_college_code(self):
        service = DictDataService()
        code = yield service.get_college_code_by_name("清华大学")
        pprint(code)
        self.assertIsInstance(code, int)

        with self.assertRaises(ValueError) as cm:
            yield service.get_college_code_by_name(None)
        self.assertEqual(cm.exception.args[0], 'invalid school_name')

        with self.assertRaises(ValueError) as cm:
            yield service.get_college_code_by_name(10101010)
        self.assertEqual(cm.exception.args[0], 'invalid school_name')

    @gen_test
    def test_college(self):
        service = DictDataService()
        colleges = yield service.get_colleges()
        # Check result
        pprint(colleges)
        self.assertIsInstance(colleges, list)

    @gen_test
    def test_retrieve_dict_of_constants(self):
        # First time, no cache
        service = DictDataService()
        ret = yield service.get_const_dict(
            parent_code=DictDataService.CONSTANT_TYPES.DEGREE_USER)
        # Check result
        pprint(ret)
        self.assertIsInstance(ret, dict)

        with self.assertRaises(ValueError) as cm:
            yield service.get_const_dict(parent_code=None)

        self.assertEqual(cm.exception.args[0], 'invalid parent_code')

if __name__ == '__main__':
    main()
