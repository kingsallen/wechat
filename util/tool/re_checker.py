# coding=utf-8

import re


class REValidator(object):

    @staticmethod
    def check_email_local(txt):
        return bool(re.match(re.compile(r'^[A-Z0-9._%+\-]{1,64}$', re.I), txt))


revalidator = REValidator()

if __name__ == '__main__':
    validator = REValidator()

    print(validator.check_email_local('ydatylmonv'))
