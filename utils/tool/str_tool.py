# coding=utf-8

def gen_salary(salary_top, salary_bottom):

    '''
    月薪
    :param salary_top:
    :param salary_bottom:
    :return:
    '''

    salary_res = "-"
    if not salary_top and not salary_bottom:
        salary_res = "面议"
    elif salary_top is None and salary_bottom is None:
        salary_res = "5k - 5k"
    elif salary_top and salary_bottom and salary_top == '999':
        salary_res = "{0}k以上".format(str(salary_bottom))
    elif salary_top and salary_bottom:
        salary_res = "{0}k - {1}k".format(str(salary_bottom), str(salary_top))

    return salary_res