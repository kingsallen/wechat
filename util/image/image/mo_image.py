# coding=utf-8

# @Time    : 1/22/17 16:12
# @Author  : towry (wanglintao@moseeker.com)
# @File    : __init__.py.py
# @DES     :

# Copyright 2016 MoSeeker

from __future__ import division
from util.image import Connector
import PIL

class MoImage(Connector):

    def __init__(self, im):
        super(MoImage, self).__init__()
        # you may want to use self.copy instead
        self._im = im
        # the processed image
        self._copy = None

    @property
    def copy(self):
        return self._copy or self._im

    @property
    def ext(self):
        format = self._im.format
        if format == 'JPEG 2000':
            return 'jpx'
        else:
            return format.lower()

    def filter_crop(self, setting=dict()):
        """
        Crop the image, box is a list with [x, y, width, height]
        :param box:
        :return:
        """
        x = setting.get('x', 0)
        y = setting.get('y', 0)
        width = setting.get('width', None)
        height = setting.get('height', None)
        load = setting.get('load', True)

        width = width if width else height
        height = height if height else width
        if not width and not height:
            width = height = _get_image_small_size(self.copy)

        self._copy = self.copy.crop((x, y, x + width, y + height))
        if load:
            self._copy.load()
        return self._copy

    def filter_resize(self, setting=dict()):
        """
        resize 过滤器会将图片缩放到给定的大小
        :param setting:
        :return:
        """
        width = setting.get('width', 1)
        height = setting.get('height', 1)
        load = setting.get('load', True)

        width = width if width else height
        height = height if height else width
        if not width and not height:
            width = height = _get_image_small_size(self.copy)

        width = int(round(width))
        height = int(round(height))

        self._copy = self.copy.resize((width, height), PIL.Image.ANTIALIAS)
        if load:
            self._copy.load()
        return self._copy

    def filter_expand(self, setting=dict()):
        """
        expand 过滤器会将图片扩大至足够大,这样后续的剪切操作不会出现剪切范围
        不够的情况.
        比如,剪切操作的大小是200x200,然而图片的大小是100x50,那么我们需要确保
        图片扩大后的高度最低是200.
        :param setting:
        :return:
        """
        width = setting.get('width', 1)
        height = setting.get('height', 1)
        load = setting.get('load', True)

        mw, mh = self.copy.size

        source_ratio = mw / mh

        if mw > width and mh > height:
            return self.copy

        expand_width = width
        expand_height = height

        expand_height = expand_width / source_ratio

        if mw < width:
            # expand width
            expand_width = width
            expand_height = expand_width / source_ratio
        if expand_height < height:
            # expand height
            expand_height = height
            expand_width = expand_height * source_ratio

        width = int(round(expand_width))
        height = int(round(expand_height))

        print ("-------------#--------------")
        print (width, height, mw, mh)

        self._copy = self.copy.resize((width, height), PIL.Image.ANTIALIAS)
        if load:
            self._copy.load()
        return self._copy


    def save_copy(self, fname, **kwargs):
        """
        Save the image
        :param fname:
        :return:
        """
        self.copy.save(fname, **kwargs)

    def get_stream(self):
        import io
        buff = io.BytesIO()

        self.copy.save(buff, self.ext, quality=90)
        buff.seek(0)
        return buff


class MoImageError(Exception):
    pass


class MoInvalidImageError(MoImageError):
    pass


def _get_image_small_size(image):
    """
    return the size of the smallest in [width, height]
    :param image:
    :return: int
    """
    width, height = image.size
    return width if width < height else height


def ext_to_format(ext):
    # fixme
    pass


def _get_resize_factor(width, height, iw, ih):
    """
    返回缩放参数, width, height 是规定缩放后的大小,但是为了保证缩放后的图片不会出现缺失情况,
    需要更改这个width, height,保证缩放后的图片的宽度高度都是最大的.
    :param width:
    :param height:
    :param iw:
    :param ih:
    :return:
    """
    if width == height:
        return (width, height, iw, ih)

