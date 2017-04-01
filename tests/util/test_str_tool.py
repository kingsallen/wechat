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


if __name__ == '__main__':
    unittest.main()
