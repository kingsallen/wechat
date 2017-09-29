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


if __name__ == '__main__':
    unittest.main()
