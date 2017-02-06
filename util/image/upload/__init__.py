# coding=utf-8

# @Time    : 1/22/17 16:12
# @Author  : towry (wanglintao@moseeker.com)
# @File    : __init__.py
# @DES     :

# Copyright 2016 MoSeeker

"""
Common upload logic placed here.
"""

from util.image.upload.qiniu_store import QiniuStore
from util.image.upload.qiniu_upload import QiniuUpload

__all__ = ['QiniuStore', 'QiniuUpload']
