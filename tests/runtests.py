# coding=utf-8

import textwrap
import unittest
import tornado.testing

TEST_MODULES = [
    'tests.page_service.test_share_chain_service'
]


def all():
    return unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)


class YiliangTextTestRunner(unittest.TextTestRunner):
    def run(self, test):
        result = super(YiliangTextTestRunner, self).run(test)
        if result.skipped:
            skip_reasons = set(reason for (test, reason) in result.skipped)
            self.stream.write(textwrap.fill(
                "Some tests were skipped because: %s" %
                ", ".join(sorted(skip_reasons))))
            self.stream.write("\n")
        return result


def main():
    kwargs = {}
    kwargs['testRunner'] = YiliangTextTestRunner

    tornado.testing.main(**kwargs)

if __name__ == "__main__":
    main()
