# coding=utf-8

from util.tool.str_tool import *
import unittest

class StrToolTestCase(unittest.TestCase):
    def test_is_odd(self):
        self.assertTrue(is_odd(1))
        self.assertTrue(is_odd(1000000001))
        self.assertTrue(is_odd('1'))
        self.assertTrue(is_odd('1000000001'))

        self.assertFalse(is_odd(2))
        self.assertFalse(is_odd(202222222222))
        self.assertFalse(is_odd('2'))
        self.assertFalse(is_odd('202222222222'))

        with self.assertRaises(ValueError):
            self.assertFalse(is_odd('abc'))

    def test_phone_number_without_country_code(self):
        self.assertTrue(phone_number_without_country_code('86-13122920190'), '13122920190')
        self.assertTrue(phone_number_without_country_code('86-13122920190'), '13122920190')
        self.assertTrue(phone_number_without_country_code('13122920190'), '13122920190')

        # with self.assertRaises(AssertionError):
        #     phone_number_without_country_code('20190')
        #
        # with self.assertRaises(AssertionError):
        #     phone_number_without_country_code('-')
        #
        # with self.assertRaises(AssertionError):
        #     phone_number_without_country_code('9873982342-03')
        #
        # with self.assertRaises(AssertionError):
        #     phone_number_without_country_code('')
        #
        # with self.assertRaises(TypeError):
        #     phone_number_without_country_code(131229231293)

    def test_ua_parser(self):
        ua1 = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_1 like Mac OS X) AppleWebKit/604.3.1 (KHTML, like Gecko) Mobile/15B5066f MicroMessenger/6.5.18 NetType/WIFI Language/zh_CN'
        ua2 = 'aaabbb'
        ua3 = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_1 like Mac OS X) AppleWebKit/604.3.1 (KHTML, like Gecko) Mobile/15B5066f MicroMessenger/6.5.18 NetType/WIFI'

        self.assertEqual(languge_code_from_ua(ua1), 'zh_CN' )
        self.assertIsNone(languge_code_from_ua(ua2))
        self.assertIsNone(languge_code_from_ua(ua3))



if __name__ == '__main__':
    unittest.main()
