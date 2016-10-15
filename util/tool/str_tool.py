# coding=utf-8

# Copyright 2016 MoSeeker


def gen_salary(salary_top, salary_bottom):
    """
    月薪
    :param salary_top:
    :param salary_bottom:
    :return:
    """

    salary_res = u"-"
    if not salary_top and not salary_bottom:
        salary_res = u"面议"
    elif salary_top is None and salary_bottom is None:
        salary_res = u"5k - 5k"
    elif salary_top and salary_bottom and salary_top == u'999':
        salary_res = u"{0}k以上".format(str(salary_bottom))
    elif salary_top and salary_bottom:
        salary_res = u"{0}k - {1}k".format(str(salary_bottom), str(salary_top))

    return salary_res
