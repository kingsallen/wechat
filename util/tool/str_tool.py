# coding=utf-8

# Copyright 2016 MoSeeker

import functools
import hashlib
import random
import re
import string
import uuid

from util.tool.iter_tool import first

import pypinyin
from pypinyin import lazy_pinyin

import conf.common as const


def password_crypt(code=None):
    """
    密码加密
    :parameter:
        code : 需要加密的密码
    :Exception:加密出错，异常上抛处理
    """
    if not code:
        code1 = "".join(random.sample('0123456789', 1))
        code2 = "".join(
            random.sample('0123456789ABCDEFGHIJKLMNOPQISTUVWXYZ', 4))
        code3 = "".join(random.sample('abcdefghijklmnopqrstuvwxyz', 1))
        code = code1 + code2 + code3

    try:
        temp_password = hashlib.md5(code.strip().encode("utf-8")).hexdigest()
        password = hashlib.sha1(temp_password.strip().encode("utf-8")).hexdigest()
        return code, password
    except Exception as e:
        raise e


def gen_salary(salary_top, salary_bottom):
    """月薪，统一由服务端返回，前端只负责展现
    :param salary_top:
    :param salary_bottom:
    :return: """
    if not salary_top and not salary_bottom:
        salary_res = "薪资面议"
    elif salary_top and salary_bottom and salary_top == 999:
        salary_res = "{0}k以上".format(int(salary_bottom))
    elif int(salary_top) == int(salary_bottom):
        salary_res = "{}k".format(int(salary_top))
    else:
        salary_res = "{0}k - {1}k".format(int(salary_bottom), int(salary_top))

    return salary_res


def gen_degree(degree, degree_above):
    """
    处理学历
    :param degree:
    :param degree_above:
    :return:
    """
    if degree and degree_above:
        return const.DEGREE.get(str(degree)) + const.POSITION_ABOVE
    elif degree:
        return const.DEGREE.get(str(degree))
    else:
        return ""


def gen_degree_v2(raw_degree, raw_degree_above, locale):
    """根据locale来拼装学历字符串"""
    degree_str = locale.translate(const.DEGREE.get(str(raw_degree)))
    above_str = ' '
    if raw_degree_above:
        above_str += locale.translate(const.POSITION_ABOVE)

    return (degree_str + above_str).strip()


def gen_experience(experience, experience_above):
    """
    处理学历要求
    :param experience:
    :param experience_above:
    :return:
    """

    if experience and experience_above:
        return experience + const.EXPERIENCE_UNIT + const.POSITION_ABOVE
    elif experience:
        return experience + const.EXPERIENCE_UNIT
    else:
        return ""


def gen_experience_v2(experience, experience_above, locale):
    """
    处理学历要求
    :param experience:
    :param experience_above:
    :param locale
    :return:
    """
    ret = ''

    if experience:
        ret = experience + " " + locale.translate(
            const.EXPERIENCE_UNIT, plural_message=const.EXPERIENCE_UNIT_PLURAL, count=experience)

    if experience_above:
        ret += " " + locale.translate(const.POSITION_ABOVE)

    return ret


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


def to_hex(text):
    return "".join("{:02x}".format(ord(c)) for c in text)


def from_hex(hex_string):
    return to_str(bytes.fromhex(hex_string))


def match_session_id(session_id):
    """从 session_id 中得到 user_id"""

    if session_id:
        session_id_list = re.match(r"([0-9]*):([0-9a-zA-Z]*)", session_id)
        return session_id_list.group(1) if session_id_list else 0
    else:
        return 0


def split(input_s, delimiter=None):
    """分割字符串成字符串数组
    """
    if not delimiter:
        delimiter = ['\r\n', '\n']

    if isinstance(delimiter, list):
        pattern = "|".join(delimiter)
    else:
        pattern = delimiter

    if not input_s:
        return list()

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

    i = i + 1 if i == len(unicode_s) - 1 else i
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


def mobile_validate(mobile):
    """
    手机号验证
    :param mobile:
    :return:
    """
    if isinstance(mobile, int):
        mobile = str(mobile)

    p = re.compile(r'^(\d+-)?(\d+)$')
    return p.match(mobile) is not None


def password_validate(password):
    """
    密码验证，必须为大于等于6位的数字和字母组合
    :param password:
    :return:
    """
    if len(password) >= 6 \
        and re.findall("[a-zA-Z]+", password) \
        and re.findall("[0-9]+", password):
        return True
    else:
        return False


def pinyin_match(text, search):
    """
    返回 text 是否和 search 匹配
    text 可以是英文,也可以是中文 text
    search 英文,中文或中文拼音

    从左往右匹配
    当两者都是汉字 或 两者都是英文 或 后者是前者的拼音时 返回 True
    """

    if text.startswith(search):
        return True

    py = functools.reduce(
        lambda x, y: x + y, lazy_pinyin(text, style=pypinyin.NORMAL))

    return py.startswith(search)


def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    return '\u4e00' <= uchar <= '\u9fff'


def is_number(uchar):
    """判断一个unicode是否是数字"""
    return '\u0030' <= uchar <= '\u0039'


def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    return ('\u0041' <= uchar <= '\u005a') or ('\u0061' <= uchar <= '\u007a')


def is_other(uchar):
    """判断是否非汉字，数字和英文字符"""
    return not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar))


def split_phone_number(phone_number):
    assert re.match(r'^(\d+-)?(\d+)$', phone_number)

    numbers = phone_number.split("-")
    if len(numbers) == 1:
        return '', numbers[0]
    elif len(numbers) == 2:
        return tuple(numbers)
    else:
        raise ValueError('phone_number(%s) format is incorrect' % phone_number)


def phone_number_without_country_code(phone_number):
    """从国家编号-电话号码中分离出电话号码"""
    return split_phone_number(phone_number)[1]


def languge_code_from_ua(useragent):
    match_obj = re.search(r'Language/(.+)', useragent)

    if match_obj:
        match = match_obj.groups()[0]

        if match.startswith('en'):
            return 'en_US'
        else:
            return 'zh_CN'

    else:
        return None


def get_uucode(lenth=36):
    """
    生成 uuid
    :param lenth:
    :return:
    """

    assert isinstance(lenth, int) and lenth <= 72, 'uucode is too long.'
    return str(uuid.uuid1())[0:lenth] if lenth < 36 else \
        (str(uuid.uuid1()) + str(uuid.uuid4()))[0:lenth]


def is_odd(obj):
    """
    check if the obj is an odd number or a string represents an odd number
    may raise value error if obj cannot be converted to int
    :param obj:
    :return:
    """
    test = int(obj)
    return test & 1 == 1


def get_send_time_from_template_message_url(url=''):
    sub = re.search(r'.*send_time=(\d+).*', url)
    if sub:
        return sub.group(1)
    else:
        return 0


def json_hump2underline(hump_json_str):
    """
    将命名为驼峰格式的转为下划线
    :param hump_json_str:
    :return:
    """
    attr_ptn = re.compile(r'"\s*(\w+)\s*"\s*:')

    # 使用hump2underline函数作为re.sub函数第二个参数的回调函数
    sub = re.sub(attr_ptn, lambda x: '"' + hump2underline(x.group(1)) + '" :', hump_json_str)
    return sub


def json_underline2hump(underline_json_str):
    """
    将命名为下划线规则的转为驼峰格式
    :param underline_json_str:
    :return:
    """
    attr_ptn = re.compile(r'"\s*(\w+)\s*"\s*:')
    sub = re.sub(attr_ptn, lambda x: '"' + underline2hump(x.group(1)) + '" :', underline_json_str)
    return sub


def underline2hump(underline_str):
    # 这里re.sub()函数第二个替换参数用到了一个匿名回调函数，回调函数的参数x为一个匹配对象，返回值为一个处理后的字符串
    sub = re.sub(r'(_\w)', lambda x: x.group(1)[1].upper(), underline_str)
    return sub


def hump2underline(hunp_str):
    # 匹配正则，匹配小写字母和大写字母的分界位置
    p = re.compile(r'([a-z]|\d)([A-Z])')
    # 这里第二个参数使用了正则分组的后向引用
    sub = re.sub(p, r'\1_\2', hunp_str).lower()
    return sub


def params_underline2hump(underline_url_params):
    """
    将命名为下划线规则的转为驼峰格式
    :param underline_url_params:
    :return:
    """
    attr_ptn = re.compile(r'(\w+)=')
    sub = re.sub(attr_ptn, lambda x: underline2hump(x.group(1)) + '=', underline_url_params)
    return sub

