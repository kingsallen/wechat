# coding=utf-8


from tornado import gen, locale
from handler.metabase import MetaBaseHandler
from util.common import ObjectDict
from util.common.decorator import check_signature
from oauth.wechat import JsApi
from util.tool.str_tool import to_str
from util.tool.url_tool import url_subtract_query

class WorkwxHandler(MetaBaseHandler):
    """Handler 基类, 仅供微信端网页调用

    不要使用（创建）get_current_user()
    get_current_user() 不能为异步方法，而 parpare() 可以
    self.current_user 将在 prepare() 中以 self.current_user = XXX 的形式创建
    Refer to:
    http://www.tornadoweb.org/en/stable/web.html#other
    """

    def __init__(self, application, request, **kwargs):
        super(WorkwxHandler, self).__init__(application, request, **kwargs)

        # 构建 session 过程中会缓存一份当前公众号信息
        self._wechat = None

    # PUBLIC API
    @check_signature
    @gen.coroutine
    def prepare(self):
        """用于生成 current_user"""
        session = ObjectDict()
        self._wechat = yield self._get_current_wechat()
        session.wechat = self._wechat
        session.wxuser = ObjectDict()
        session.qxuser = ObjectDict()
        yield self._add_company_info_to_session(session)
        session.sysuser = ObjectDict()
        self._workwx = yield self.workwx_ps.get_workwx(session.company.id, session.company.hraccount_id)
        session.workwx = self._workwx
        self._add_jsapi_to_wechat(session.wechat)
        self.current_user = session  #前端用

        client_env = ObjectDict({"name": self._client_env})
        self.namespace = {"client_env": client_env} #前端用

        # 内存优化
        self._wechat = None
        self._workwx = None

        self.logger.debug("current_user:{}".format(self.current_user))
        self.logger.debug("+++++++++++++++WORKWX PREPARE OVER+++++++++++++++++++++")

    @gen.coroutine
    def _get_current_wechat(self, qx=False):
        if qx:
            signature = self.settings['qx_signature']
        else:
            signature = self.params['wechat_signature']
        wechat = yield self.wechat_ps.get_wechat(conds={
            "signature": signature
        })
        if not wechat:
            self.write_error(http_code=404)
            return

        raise gen.Return(wechat)

    @gen.coroutine
    def _add_company_info_to_session(self, session):
        """拼装 session 中的 company, employee
        """

        session.company = yield self._get_current_company(session.wechat.company_id)

        # if session.sysuser.id and self.is_platform:
        #     employee = yield self.user_ps.get_valid_employee_by_user_id(
        #         user_id=session.sysuser.id, company_id=session.company.id)
        #     session.employee = employee

    @gen.coroutine
    def _get_current_company(self, company_id):
        """获得企业母公司信息"""

        conds = {'id': company_id}
        company = yield self.company_ps.get_company(conds=conds, need_conf=True)

        # 配色处理，如果theme_id为5表示公司使用默认配置，不需要将原始配色信息传给前端
        # 如果将theme_id为5的传给前端，会导致前端颜色无法正常显示默认颜色
        if company.conf_theme_id != 5 and company.conf_theme_id:
            theme = yield self.wechat_ps.get_wechat_theme(
                {'id': company.conf_theme_id, 'disable': 0})
            if theme:
                company.update({
                    'theme': [
                        theme.background_color,
                        theme.title_color,
                        theme.button_color,
                        theme.other_color
                    ]
                })
        else:
            company.update({'theme': None})

        raise gen.Return(company)

    def _add_jsapi_to_wechat(self, wechat):
        """拼装 jsapi"""
        wechat.jsapi = JsApi(
            jsapi_ticket=wechat.jsapi_ticket,
            url=self.fullurl(encode=False))

    def fullurl(self, encode=True):
        """
        获取当前 url， 默认删除 query 中的 code 和 state。

        和 oauth 有关的 参数会影响 prepare 方法
        :param encode: False，不会 Encode，主要用在生成 jdsdk signature 时使用
        :return:
        """

        full_url = to_str(self.request.full_url())

        if not self.host in self.request.full_url():
            full_url = full_url.replace(self.settings.m_host, self.host)

        # if not self.domain in self.request.full_url():
        #     full_url = full_url.replace(self.settings.m_domain, self.domain)

        if not encode:
            return full_url
        return url_subtract_query(full_url, ['code', 'state'])
