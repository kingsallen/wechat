# coding=utf-8

# @Time    : 1/22/17 16:12
# @Author  : towry (wanglintao@moseeker.com)
# @File    : __init__.py.py
# @DES     :

# Copyright 2016 MoSeeker

from util.image import Connector

class BaseUpload(Connector):
    """
    上传基类
    需要一个配置来进行上传
    """
    def __init__(self, _init_params=dict()):
        super(BaseUpload, self).__init__()
        self._init_params = _init_params
        self._image = None

    @property
    def params(self):
        return self._init_params

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        self._image = image

    def _do_upload(self):
        raise NotImplementedError()

    def _check_size(self, _size):
        max_size = self.params.get('max_filesize', 1024 * 1024 * 4)
        if _size > max_size:
            return UploadResult(message=u"文件大小大于上传上线: {}mb".format(max_size / 1024 / 1024))
        return None

    def _before_upload(self):
        """
        process the image before upload or save,
        you can pass ignored in the subclass to skip some process.
        :param ignored:
        :return:
        """
        filters = self.params.get('before_upload', None)

        if filters:
            length = len(filters)
            index = 0
            for filter in filters:
                _setting = self.params.get("filter_{}".format(filter), dict())
                if index != length - 1:
                    # disable image load
                    _setting['load'] = False
                else:
                    _setting['load'] = True
                index += 1
                self._apply_filter(filter, _setting)

    def _apply_filter(self, filter, setting=dict()):
        """
        Apply the filter function in image, to resize, or crop the image.
        :param filter: string
        :param setting: dict
        :return:
        """
        filter_parent = self.image

        _attr = "filter_{}".format(filter)
        m = getattr(filter_parent, _attr) if hasattr(filter_parent, _attr) else None
        if m is None or not hasattr(m, '__call__'):
            raise NameError("apply filter failed, no such filter {}".format(_attr))
        self.logger.info("[apply filter] - use filter {}".format(_attr))
        m(setting)

class UploadResult(object):
    def __init__(self, status=1, message=None, data=None, exception=None):
        self._status = status
        self._data = data
        self._exception = exception
        self._message = message or u"上传图片时发生未知错误"
        if self._data is not None:
            self._status = 0

    @property
    def status(self):
        return self._status
    @property
    def message(self):
        return self._message

    @property
    def data(self):
        return self._data

    @property
    def exception(self):
        return self._exception
