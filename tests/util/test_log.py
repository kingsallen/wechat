# coding=utf-8

import unittest
import shutil
from util.common.log import Logger
import os

TEST_LOGS = "/tmp/test_logs/"


class TestLogger(unittest.TestCase):

    def tearDown(self):
        shutil.rmtree(TEST_LOGS)

    def setUp(self):
        if not os.path.exists(TEST_LOGS):
            os.makedirs(TEST_LOGS)

    def test_debug(self):
        logger = Logger(TEST_LOGS)
        logger.debug("test debug")
        with open(TEST_LOGS + "debug/debug.log") as log:
            text = log.readline()
            self.assertTrue("DEBUG" in text)
            self.assertTrue("test debug" in text)

    def test_info(self):
        logger = Logger(TEST_LOGS)

        logger.info("test info")
        with open(TEST_LOGS + "info/info.log") as log:
            text = log.readline()
            self.assertTrue("INFO" in text)
            self.assertTrue("test info" in text)

    def test_warning(self):
        logger = Logger(TEST_LOGS)

        logger.warning("test warn")
        with open(TEST_LOGS + "warn/warn.log") as log:
            text = log.readline()
            self.assertTrue("WARN" in text)
            self.assertTrue("test warn" in text)

    def test_error(self):
        logger = Logger(TEST_LOGS)

        logger.error("test error")
        with open(TEST_LOGS + "error/error.log") as log:
            text = log.readline()
            self.assertTrue("ERROR" in text)
            self.assertTrue("test error" in text)

    def test_stats(self):
        logger = Logger(TEST_LOGS)

        logger.stats("test stats")
        with open(TEST_LOGS + "stats/stats.log") as log:
            text = log.readline()
            self.assertTrue("STATS" in text)
            self.assertTrue("test stats" in text)
