# coding=utf-8

try:
    import ujson as json
except ImportError:
    import json

import importlib

import tornado
import tornado.web
import tornado.gen

# import constant
from utils.jsonutil import JSONEncoder

# class Apis(object):
#     def __init__(self, jsapi_ticket, url, **kwargs):
#         self.sign = Sign(jsapi_ticket=jsapi_ticket)
#         self.__dict__.update(self.sign.sign(url=url))


class BaseHandler(tornado.web.RequestHandler):

    @property
    def logger(self):
        return self.application.logger

    @property
    def settings(self):
        return self.application.settings

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.json_args = None
        self.params = None

        # if self.settings.get("session"):
        #     self.session = session.Session(self.application.session_manager, self, 1)
        #     self.session.save()

        # 日志变量
        self.log_info = {}

        # # pageservice实例化
        # message_ps = importlib.import_module('service.page.{0}.{1}'.format('common', 'message'))
        # laboratory_ps = importlib.import_module('service.page.{0}.{1}'.format('common', 'laboratory'))
        # hr_account_ps = importlib.import_module('service.page.{0}.{1}'.format('hr', 'hr_account'))
        #
        # position_ps = importlib.import_module('service.page.{0}.{1}'.format('job', 'position'))
        # company_ps = importlib.import_module('service.page.{0}.{1}'.format('job', 'company'))
        # user_position_ps = importlib.import_module('service.page.{0}.{1}'.format('job', 'user_position'))
        # wechat_ps = importlib.import_module('service.page.{0}.{1}'.format('job', 'wechat'))
        #
        # self.message_ps = getattr(message_ps, 'MessagePageService')()
        # self.laboratory_ps = getattr(laboratory_ps, 'LaboratoryPageService')()
        # self.hr_account_ps = getattr(hr_account_ps, 'HrAccountPageService')()
        # self.position_ps = getattr(position_ps, 'PositionPageService')()
        # self.company_ps = getattr(company_ps, 'CompanyPageService')()
        # self.user_position_ps = getattr(user_position_ps, 'UserPositionPageService')()
        # self.wechat_ps = getattr(wechat_ps, 'WechatPageService')()
        #
        # self.image_base = self.get_image_base()
        # self.stats_base = self.get_stats_base()

    # def _get_current_wechat(self):
    #
    #     wechat = mdict(default='')
    #     if self.settings.get("session"):
    #         wechat_signature = self.get_argument('wechat_signature', self.settings.get("qx_wechat_signature"))
    #         wechat_session = self.application.session_manager.redis.get(wechat_signature)
    #         if wechat_session:
    #             wechat = mdict(ujson.loads(wechat_session), default='')
    #
    #     if not wechat:
    #         req_url = self.request.protocol + "://" + self.request.host + self.request.uri
    #
    #     jsapi = Apis(jsapi_ticket=wechat._jsapi_ticket, url=self.request.protocol + '://'+ self.request.host + self.request.uri)
    #     wechat.jsapi=jsapi
    #     return wechat
    #
    # def get_current_user(self):
    #
    #     return self._get_current_wechat()

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

        """
        :param fields_mapping 校验类型。会过滤HTML标签
        usage:
            对输入参数做检查，主要用于post、put

            try:
                self.guarantee("mobile", "name", "password")
            except AttributeError:
                return

            mobile = self.params["mobile"]
        """

        self.params = dict()
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
        """
        结果输出，根据response中的Accept来决定输出为render or json
        :param template_name:
        :param kwargs:
        :return:
        """
        try:
            if "application/json" in self.request.headers.get("Accept", ""):
                self.send_json(kwargs)
            else:
                self.render(template_name, status_code=200, **kwargs)
        except Exception as e:
            self.logger.error(e)

    def send_json_warn(self, chunk):
        """
        请求成功，但业务逻辑错误
        :param chunk:

        usage:
            416（参数错误，或不符合业务逻辑的返回）Requested Range Not Satisfiable

        reutrn:
            {
                "msg": success or 错误信息
            }
        """
        self.send_json(chunk, status_code=416)

    def write_error(self, status_code, **kwargs):

        """
        错误页
        :param status_code: http_status
        :param kwargs:
        :return:

        usage：
            403 Forbidden
            404 Resource not found
            500 Internal server error
        """
        # TODO yiliang
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
        """
        页面渲染,只接受status_code=200|416信息
        :param status_code: http_status
        :param template_name: 模板地址
        :param kwargs:
        :return:

        usage：
            200 Success
            416 Requested Range Not Satisfiable
        """
        self.add_log({"res_type": "html"})
        self.set_status(status_code)
        super(BaseHandler, self).render(template_name, **kwargs)
        return

    def send_json(self, chunk, status_code=200):
        """
        用于发送含有 objectid 数据类型的数据
        :param chunk:
        :return:
            {
                "msg": success or 错误信息
                "data": []
            }
        """

        self.add_log({"res_type": "json"})
        chunk = JSONEncoder().encode(chunk)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_status(status_code)
        self.write(chunk)
        return

    def send_log(self):
        """
        日志打印
        :return:
        """

        info = {
            "handler": __name__ + '.' + self.__class__.__name__,
            "module": self.__class__.__module__.split(".")[1],
            "status_code": self.get_status(),
        }
        if self.log_info:
            info.update(self.log_info)

        self.logger.record(self, info)

    def add_log(self, log):
        """
        手动添加日志字段
        :return:
        """
        if not self.log_info:
            self.log_info = {}
        if isinstance(log, dict):
            self.log_info.update(log)

    def get_image_base(self):
        """
        JS拼装静态资源url
        :return:
        """
        ret = self.settings["static_domain"]
        if self.settings["debug"]:
            ret = ""
        return ret

    def get_stats_base(self):
        """
        页面点击统计脚本，请求位置
        """
        ret = self.settings["original_static_domain"]

        return ret

    def static_url(self, path, include_host=None, protocol="//", **kwargs):
        """
        获取静态资源的url
        * debug状态下，使用本地路径
        * 非debug状态下，使用static_domain配置域名下路径
        """

        if self.settings["debug"]:
            return super(BaseHandler, self).static_url(
                path, include_host, **kwargs)
        else:
            static_domain = self.settings["static_domain"]
            return protocol + static_domain + "/" + path
