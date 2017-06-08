# coding=utf-8

import string
import random
import io

import tornado.gen

from captcha.image import ImageCaptcha
from handler.base import BaseHandler
from util.common.decorator import handle_response
from util.tool.str_tool import to_str
from globals import redis

import conf.common as const


class CaptchaMixin(object):
    # 宽度和高度符合比例即可，
    # 这个像素值可以保证满足最大屏手机也看得清楚
    WIDTH = 214
    HEIGHT = 80

    LENGTH = 4

    # 随机字体大小
    FONT_SIZE= (60, 70, 80)

    # 似乎用多一点的字体可以更难破解，但是会消耗更多内存
    FONTS = [
        'DejaVuSans - Bold.ttf',
        'DejaVuSansMono - Bold.ttf',
        'DejaVuSansMono.ttf',
        'DejaVuSans.ttf',
        'DejaVuSerif - Bold.ttf',
        'DejaVuSerif.ttf'
    ]

    # 去除比较难辨认的字母数字，节省公司的短信开销
    CHARS = set(string.ascii_letters + string.digits) - set('Oo0i1l2zZ')

    _image_captcha = ImageCaptcha(width=WIDTH, height=HEIGHT,
                                  fonts=FONTS, font_sizes=FONT_SIZE)

    def captcha_generate(self):
        """随机生成验证码图片和字符串
        """
        vcode = random.sample(self.CHARS, self.LENGTH)
        return self._image_captcha.generate_image(vcode), vcode

    def captcha_save(self, session_id, user_id, code):
        """将生成的验证码写入 redis
        """
        if not any([session_id, user_id, code]):
            return False

        # 验证码存入 WECHAT_VCODE_:SESSION_ID_:USER_ID, TTL 60
        redis.set(self.make_key(session_id, user_id), code, ttl=60)
        return True

    def captcha_check(self, session_id, user_id, code):
        """ 校验验证码，无论是否正确，删除缓存中的验证码（one time code）       
        """
        if not any([session_id, user_id, code]):
            return False

        key = self.make_key(session_id, user_id)
        cached_code = redis.get(key)

        if not cached_code:
            return False

        check_result = to_str(cached_code).lower() == code.lower()
        redis.delete(key)

        return check_result

    @staticmethod
    def make_key(session_id, user_id):
        return "VCODE_{}_{}".format(session_id, user_id)


class CaptchaHandler(CaptchaMixin, BaseHandler):
    """ 生成 captcha
    """

    @handle_response
    @tornado.gen.coroutine
    def get(self):
        img, vcode = self.captcha_generate()
        mstream = io.BytesIO()
        img.save(mstream, "PNG")

        # 生成验证码并 finish
        self.set_header("Content-type", "image/png")
        self.write(mstream.getvalue())
        self.finish()

        session_id = to_str(
            self.get_secure_cookie(const.COOKIE_SESSIONID) or
            self.get_secure_cookie(const.COOKIE_MVIEWERID) or ''
        )

        self.captcha_save(session_id, self.current_user.sysuser.id, vcode)
