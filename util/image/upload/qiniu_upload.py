# coding=utf-8

# @Time    : 1/22/17 16:12
# @Author  : towry (wanglintao@moseeker.com)
# @File    : __init__.py.py
# @DES     :

# Copyright 2016 MoSeeker

import os
import time
import random
import string
from PIL import Image
from util.image.upload import QiniuStore
from util.image.upload.base import UploadResult
from util.image.upload.base import BaseUpload
from util.image.image.mo_image import MoImage
from setting import settings

QINIU_AK = settings.get('qiniu_ak', 'rMkcbmVYotu9Zxi0MqjmP5EFy6a9sZ5-h78Qt5GV')
QINIU_SK = settings.get('qiniu_sk', 'n8qRg0VJBsGyHlZJh1W887LDn2Z-2gbavg9xgoRP')
QINIU_BUCKET = settings.get('qiniu_bucket', 'moseekertest')

try:
    basestring
except NameError:
    basestring = str

class QiniuUpload(BaseUpload):
    """
    params:
    - filename
    - filename_prefix
    - max_size
    """

    def __init__(self, _init_params = dict()):
        super(QiniuUpload, self).__init__(_init_params)

    def upload_bytes(self, content):
        import io

        """
        上传文件，从文件内容进行上传，适用于表单的上传.
        如果你要其他的上传方式，可以在这里添加你的上传方式.
        """
        buff = io.BytesIO()
        buff.write(content)

        # get file size
        buff.seek(0, os.SEEK_END)
        check = self._check_size(buff.tell())

        # go back to start
        buff.seek(0)

        if check:
            return check

        try:
            im = Image.open(buff)
        except IOError as e:
            return QiniuUploadResult(message=u"上传失败,请尝试换一个图片", exception=e)

        self.image = MoImage(im)
        self.image.set_logger(self.LOG)

        self._before_upload()
        result = self._do_upload()
        return result

    def _do_upload(self, filename=None):
        store_settings = dict()
        store_settings['qiniu_ak'] = QINIU_AK
        store_settings['qiniu_sk'] = QINIU_SK
        store = QiniuStore(store_settings)

        fname = self.params.get('filename', None)
        if not fname:
            raise QiniuUploadError("upload require a filename from the upload settings")

        fname = _safe_filename(fname)

        bucket = store.get_bucket(QINIU_BUCKET)
        key = bucket.upload_stream(_get_random_filename(fname, self.params.get('filename_prefix', 'upload')),
                                   self.image.get_stream())

        return QiniuUploadResult(data=key)


class QiniuUploadResult(UploadResult):
    pass


class QiniuUploadError(Exception):
    pass


def _get_filename_ext(filename):
    name = os.path.basename(filename)
    return os.path.splitext(name)


def _get_random_filename(filename, prefix=""):
    assert isinstance(prefix, basestring)
    name = _get_filename_ext(filename)
    ext = name[1]
    fname = _id_generator(size=10)
    rstr = str(int(time.time()))
    return os.path.join(prefix, fname + "-" + rstr + ext)


def _safe_filename(filename, max_length=20):
    keepcharacters = ('-','.','_')
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()

def _id_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
