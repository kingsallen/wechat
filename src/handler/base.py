# coding=utf-8

try:
    import ujson as json
except ImportError:
    import json

import tornado.web
from tornado.util import ObjectDict
from utils.jsonutil import JSONEncoder
from utils.session import Session


class BaseHandler(tornado.web.RequestHandler):

    # Initialization and properties
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.json_args = None
        self.params = None
        self._log_info = None

        if self.settings.get("session"):
            self.session = Session(self.application.session_manager, self, 1)
            self.session.save()
        # 日志变量
        # pageservice实例化

    @property
    def logger(self):
        return self.application.logger

    @property
    def settings(self):
        return self.application.settings

    @property
    def log_info(self):
        if self._log_info and dict(self._log_info):
            return self._log_info
        return None

    @log_info.setter
    def log_info(self, value):
        if dict(value):
            self._log_info = dict(value)

    # Public API
    def prepare(self):
        self.json_args = None
        headers = self.request.headers
        try:
            if("application/json" in headers.get("Content-Type", "") and
               self.request.body != ""):
                self.json_args = json.loads(self.request.body)
        except Exception as e:
            self.logger.error(e)

    def guarantee(self, fields_mapping, *args):
        self.params = {}
        for arg in args:
            try:
                self.params[arg] = self.json_args[arg]
                self.json_args.pop(arg)
            except KeyError:
                ret_field = fields_mapping.get(arg, arg)
                raise AttributeError(u"{0}不能为空".format(ret_field))
            self.params.update(self.json_args)

        return self.params

    def output(self, template_name='', **kwargs):
        try:
            if "application/json" in self.request.heaers.get("Accept", ""):
                self.send_json(kwargs)
            else:
                self.render(template_name, status_code=200, **kwargs)
        except Exception as e:
            self.logger.error(e)

    def send_json_warn(self, chunk):
        self.send_json(chunk, status_code=416)

    def write_error(self, status_code, **kwargs):

        if status_code == 403:
            self.render('error/404.html',
                        status_code=status_code,
                        message="",
                        title=status_code)
        elif status_code == 404:
            self.render('error/404.html',
                        status_code=status_code,
                        message="",
                        title=status_code)
        else:
            self.render('error/500.html',
                        status_code=status_code,
                        message="",
                        title=status_code)

    def render(self, template_name, status_code=200, **kwargs):
        self.log_info = {"res_type": "html"}
        self.set_status(status_code)
        super(BaseHandler, self).render(template_name, **kwargs)
        return

    def send_json(self, chunk, status_code=200):
        self.log_info = {"res_type": "json"}
        chunk = JSONEncoder().encode(chunk)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_status(status_code)
        self.write(chunk)
        return

    def get_image_base(self):
        ret = self.settings["static_domain"]
        if self.settings["debug"]:
            ret = ""
        return ret

    def get_stats_base(self):
        ret = self.settings["original_static_domain"]
        return ret

    def static_url(self, path, include_host=None, protocol="//", **kwargs):
        if self.settings["debug"]:
            return super(BaseHandler, self).static_url(
                path, include_host, **kwargs)
        else:
            static_domain = self.settings["static_domain"]
            return protocol + static_domain + "/" + path

    # priviate methods
    def _send_log(self, ):
        info = ObjectDict(
            handler=__name__ + '.' + self.__class__.__name__,
            module=self.__class__.__module__.split(".")[1],
            status_code=self.get_status()
        )
        info.update(self.log_info)

        self.logger.record(
            json.dumps(self._get_info_header(info), ensure_ascii=0))

    def _get_info_header(self, log_params):
        request = self.request
        req_params = request.arguments

        if req_params and req_params.get('password', 0) != 0:
            req_params['password'] = 'xxxxxx'

        log_info_common = ObjectDict(
            useragent=request.headers.get('User-Agent'),
            referer=request.headers.get('Referer'),
            remote_ip=(
                request.headers.get('Remoteip') or
                request.headers.get('X-Forwarded-For') or
                request.remote_ip
            ),
            req_type=request.method,
            req_uri=request.uri,
            session_id=self.get_secure_cookie('session_id'),
        )

        log_info_common.update(req_params)
        log_params.update(log_info_common)

        return JSONEncoder().encode(log_params)