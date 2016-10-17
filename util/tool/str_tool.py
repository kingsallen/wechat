# coding=utf-8

# Copyright 2016 MoSeeker

def gen_salary(salary_top, salary_bottom):
    """
    月薪
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

def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode('utf-8')
    else:
        value = bytes_or_str
    return value  # Instance of str


def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode('utf-8')
    else:
        value = bytes_or_str
    return value  # Instance of bytes


def encrypt_unionid(p):
    ret = ""
    for c in p:
        ret += str(ord(c))+'m'
    return ret


def decrypt_unionid(p):
    ret = ""
    for i in p.split("m"):
        if i:
            ret += chr(int(i))
    return ret

if __name__ == "__main__":
    e = encrypt_unionid("o6_bmasdasdsad6_2sgVt7hMZOPfL")
    print(e)
    d = decrypt_unionid(e)
    print(d)
