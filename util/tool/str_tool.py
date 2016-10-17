# coding=utf-8

# Copyright 2016 MoSeeker


def gen_salary(salary_top, salary_bottom):
    """
    月薪，统一由服务端返回，前端只负责展现
    :param salary_top:
    :param salary_bottom:
    :return:
    """

    if not salary_top and not salary_bottom:
        salary_res = "面议"
    elif salary_top and salary_bottom and salary_top == 999:
        salary_res = "{0}k以上".format(int(salary_bottom))
    else:
        salary_res = "{0}k - {1}k".format(int(salary_bottom), int(salary_top))

    return salary_res
