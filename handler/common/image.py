# coding=utf-8

import urllib.parse

from tornado import gen, httpclient

from handler.base import BaseHandler
from util.common.decorator import handle_response
from util.tool.url_tool import make_static_url


class ImageFetchHandler(BaseHandler):
    """GET 请求获取 一个 image 并返回，主要用来清除 header 中的 referrer，
    目的是逃过防盗链检查
    """
    @handle_response
    @gen.coroutine
    def get(self):
        file_id = self.get_argument("id_photo_url", None) # 身份证组件照片显示：id_photo_url数据库中照片存放的id, 通过id找到绝对路径
        url = self.get_argument("url", None)
        if not url and not file_id:
            self.write_error(http_code=404)
            return

        if file_id:
            id_photo_url = yield self.user_ps.get_custom_file(file_id, self.current_user.sysuser.id)
            binfile = open(id_photo_url.url, 'rb')
            content = binfile.read()
        else:
            url = make_static_url(urllib.parse.unquote_plus(url), ensure_protocol=True)

            headers = {"Referer": ""}
            data = yield httpclient.AsyncHTTPClient().fetch(url, headers=headers)
            content = data.body
        self.set_header("Content-Type", "image/jpeg")
        self.write(content)
