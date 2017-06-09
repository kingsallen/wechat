# coding=utf-8

from captcha.image import ImageCaptcha

import random
import string
import pathlib

from unittest import TestCase


class CaptchaTestCase(TestCase):
    ic = ImageCaptcha(width=214, height=80)

    letters_all = set(string.ascii_letters + string.digits)
    letters_exclueded = set('Oo01l')
    letters = letters_all - letters_exclueded

    def test_captcha_gen_file(self):
        path_str = '/tmp/out.png'
        code = random.sample(self.letters, 4)
        self.ic.write(code, path_str)
        out = pathlib.Path(path_str)
        self.assertTrue(out.is_file())
