# coding=utf-8

# @Time    : 1/22/17 16:12
# @Author  : towry (wanglintao@moseeker.com)
# @File    : __init__.py
# @DES     :

# Copyright 2016 MoSeeker

import os
import qiniu
from util.image import Connector

try:
    basestring
except NameError:
    basestring = str

__all__ = ['QiniuStore', 'QiniuStoreError']


class QiniuStore(Connector):
    """
    Qiqiu python sdk documentation: http://developer.qiniu.com/code/v7/sdk/python.html
    """

    def __init__(self, qiniu_sk, qiniu_ak):
        """Qiniu required settings, qiniu app key and qiniu secret key.
        :param qiniu_sk:
        :param qiniu_ak:
        :return: None
        """
        super(QiniuStore, self).__init__()
        self._qiniu_sk = qiniu_sk
        self._qiniu_ak = qiniu_ak
        self._store = dict()

        # missing qiniu app key and qiniu secret key
        if not self._qiniu_ak or not self._qiniu_sk:
            raise QiniuStoreError("QiniuStore requires appkey:qiniu_ak and secretkey: qiniu_sk.")

        self._qiniu = qiniu.Auth(self._qiniu_ak, self._qiniu_sk)

    def get_bucket(self, bucket_name):
        """
        Return a bucket for upload, bucket is the space you want to upload to in
        qiniu server.
        :param bucket_name: The qiniu space name.
        :return: QiniuBucket
        """
        if not isinstance(bucket_name, basestring):
            raise QiniuStoreError("bucket_name must be a string, found {}".format(type(bucket_name)))

        return QiniuBucket(self, bucket_name)

    def get_token(self, bucket_name, key, timeout=3600):
        """
        Get qiniu upload token
        :param bucket_name: the space name to upload to.
        :param key: The path of the file name in qiniu space after uploaded.
        :param timeout: you may ignore this or look up the document by yourself.
        :return: string
        """
        return self._qiniu.upload_token(bucket_name, key, timeout)

    def upload_file(self, token, key, file):
        """
        upload file to qiniu
        :param token: the upload token, generated from bucket.
        :param key: the file path in qiniu server.
        :param file: the file path in local.
        :return:
        """
        if not os.path.exists(file):
            raise QiniuStoreError("the local file not exists: {}".format(file))
        ret, info = qiniu.put_file(token, key, file)
        return ret, info

    def upload_stream(self, token, key, stream):
        """
        upload data to qiniu
        :param token:
        :param key:
        :param stream:
        :return:
        """
        if not hasattr(stream, 'read'):
            raise QiniuStoreError("upload_stream need a file like object")
        data = stream.read()
        ret, info = qiniu.put_data(token, key, data)
        return ret, info

    def put(self, key, ret):
        """
        Store the ret information, used by the bucket
        :param key: the filepath in qiniu path
        :param ret: dict, {key: ..., hash: ...}
        :return:
        """
        self._store[key] = ret

    def get(self, key, default=dict()):
        return self._store.get(key, default)


class QiniuBucket(object):
    """
    Qiniu bucket class.
    Use this to upload images to qiniu.
    """

    def __init__(self, store, bucket_name):
        self._store = store
        self._bucket_name = bucket_name
        self._result = None

    def upload(self, key, file):
        """
        upload image to qiniu
        :param key: the path of the file in qiniu.
        :param file: the file path in local.
        :return:
        """
        token = self._store.get_token(self._bucket_name, key)
        # upload the file
        ret, info = self._store.upload_file(token, key, file)
        _key = ret.get('key', None)
        if _key != key:
            raise QiniuStoreError("upload to qiniu failed, {0} != {1}".format(_key, key))
        # ret is all we need {key: ..., hash: ...}
        self._store.put(key, ret)
        return _key

    def upload_stream(self, key, stream):
        """
        upload image by stream, it's faster
        :param key:
        :param stream:
        :return:
        """
        token = self._store.get_token(self._bucket_name, key)
        ret, info = self._store.upload_stream(token, key, stream)
        _key = ret.get('key', None)
        if _key != key:
            raise QiniuStoreError("upload to qiniu failed, {0} != {1}".format(_key, key))
        self._store.put(key, ret)
        return _key

class QiniuStoreError(Exception):
    """QiniuStore exception
    """
    pass
