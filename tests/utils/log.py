# coding=utf-8

# Copyright 2016 MoSeeker

import unittest
import shutil
from util.common.log import Logger

TEST_LOGS = "/tmp/test_logs/"


class LogTestCase(unittest.TestCase):

    def test_debug(self):
        shutil.rmtree(TEST_LOGS)

        logger = Logger(TEST_LOGS)
        logger.debug("test debug")

        with open(TEST_LOGS + "debug/debug.log") as log:
            text = log.readline()
            self.assertTrue("DEBUG" in text)
            self.assertTrue("test debug" in text)

    def test_info(self):
        shutil.rmtree(TEST_LOGS)

        logger = Logger(TEST_LOGS)

        logger.info("test info")
        with open(TEST_LOGS + "info/info.log") as log:
            text = log.readline()
            self.assertTrue("INFO" in text)
            self.assertTrue("test info" in text)

    def test_warn(self):
        shutil.rmtree(TEST_LOGS)

        logger = Logger(TEST_LOGS)

        logger.warn("test warn")
        with open(TEST_LOGS + "warn/warn.log") as log:
            text = log.readline()
            self.assertTrue("WARN" in text)
            self.assertTrue("test warn" in text)

    def test_error(self):
        shutil.rmtree(TEST_LOGS)

        logger = Logger(TEST_LOGS)

        logger.error("test error")
        with open(TEST_LOGS + "error/error.log") as log:
            text = log.readline()
            self.assertTrue("ERROR" in text)
            self.assertTrue("test error" in text)

    def test_customer(self):
        shutil.rmtree(TEST_LOGS)

        logger = Logger(TEST_LOGS)

        logger.record("test customer")
        with open(TEST_LOGS + "customer/customer.log") as log:
            text = log.readline()
            self.assertTrue("CUSTOMER" in text)
            self.assertTrue("test customer" in text)

if __name__ == "__main__":
    unittest.TestLoader().loadTestsFromTestCase(LogTestCase).run()
