# coding=utf-8

# Copyright 2016 MoSeeker

import re
import random
import string


def gen_salary(salary_top, salary_bottom):
    """月薪，统一由服务端返回，前端只负责展现
    :param salary_top:
    :param salary_bottom:
    :return: """
    if not salary_top and not salary_bottom:
        salary_res = "面议"
    elif salary_top and salary_bottom and salary_top == 999:
        salary_res = "{0}k以上".format(int(salary_bottom))
    else:
        salary_res = "{0}k - {1}k".format(int(salary_bottom), int(salary_top))

    return salary_res


def to_str(bytes_or_str):
    """to Python 3 str type"""
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode('utf-8')
    else:
        value = bytes_or_str
    return value  # Instance of str


def to_bytes(bytes_or_str):
    """to Python 3 bytes type"""
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode('utf-8')
    else:
        value = bytes_or_str
    return value  # Instance of bytes


def to_hex(string):
    return "".join("{:02x}".format(ord(c)) for c in string)


def from_hex(hex_string):
    return to_str(bytes.fromhex(hex_string))


def split(input_s, delimiter=None):
    """分割字符串成字符串数组
    """
    if not delimiter:
        delimiter = ['\r\n', '\n']

    if isinstance(delimiter, list):
        pattern = "|".join(delimiter)
    else:
        pattern = delimiter

    try:
        ret = [line.strip() for line in re.split(pattern, input_s)]
    except Exception:
        ret = [input_s]
    return ret


def trunc(s, limit, coding="UTF-8", postfix="..."):
    """trancate a long string with postfix"""
    unicode_s = s.decode(coding) if type(s) == bytes else s
    nums = (len(u.encode(coding)) for u in unicode_s)
    sum, i = 0, 0
    use_postfix = ""
    for i, n in enumerate(nums):
        if sum + n > limit:
            use_postfix = postfix
            break
        else:
            sum += n
    return unicode_s[:i] + use_postfix


def set_literl(l):
    """list 输出左右为小括号的字符串 (set 标准输出)"""
    ret = None
    if isinstance(l, list):
        ret = "(%s)" % l.__repr__()[1:-1]
    return ret


def generate_nonce_str(length=32, upper=True):
    """
    根据微信支付接口需要生成随机字符串,不长于32位
    :param length: 随机字符串长度,默认为32
    :return: 生成的随机字符串
    """
    ret = ''.join(
        random.sample(string.ascii_letters + string.digits, length))
    if upper:
        ret = ret.upper()
    return ret

def add_item(d, k, v=None, strict=True):
    '''
    :param d:  原始字典
    :param k:  添加的key名称
    :param v:  添加的value 名称
    :param strict: 是否做判断(默认将value有值的情况才会添加)
    :return: False: 原来有这个key, True: 原来没有这个Key
    '''
    if not isinstance(d, dict):
        raise TypeError('can only operate dict.')
    if strict is False:
        return d.setdefault(k, v) == v
    if strict is True and v:
        return d.setdefault(k, v) == v
    return None

def email_validate(email):
    """邮箱验证
    :param email:
    :return:
    """
    result = re.match(r"^[A-Za-z0-9_\-\.]*@([-A-Za-z0-9]+\.)+[A-Za-z]*", email)
    if result:
        return result.group(0) == email
    else:
        return False

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if '\u4e00' <= uchar <= '\u9fff':
        return True
    else:
        return False

def is_number(uchar):
    """判断一个unicode是否是数字"""
    if '\u0030' <= uchar <= '\u0039':
        return True
    else:
        return False

def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if ('\u0041' <= uchar <= '\u005a') or ('\u0061' <= uchar <= '\u007a'):
        return True
    else:
        return False

def is_other(uchar):
    """判断是否非汉字，数字和英文字符"""
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False


if __name__ == '__main__':

    print (is_chinese("中国人"))
    print (is_chinese("中国人 chinese"))
    print (is_chinese("chinese"))
    print (is_number("123abs"))
    print (is_alphabet("chine china"))
    print (is_alphabet("中国人"))
    print (is_chinese(""))
    print (is_alphabet("6789dgagh"))
    print (to_str("jiu "))
    print (to_str(" jid"))
    print (to_str("j dfd"))

