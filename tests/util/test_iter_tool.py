# coding=utf-8

import util.tool.iter_tool as iter_tool
import unittest


class IterToolTestCase(unittest.TestCase):
    def test_dedup_list(self):
        list1 = [[1, 2], [1, 2], [1], [1, 2, 3]]
        list2 = iter_tool.list_dedup_list(list1)
        self.assertEquals(list2, [[1, 2], [1], [1, 2, 3]])
