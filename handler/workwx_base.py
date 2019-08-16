# coding=utf-8


from tornado import gen, locale
from handler.metabase import MetaBaseHandler
from util.common import ObjectDict
from util.common.decorator import check_signature


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
        self.current_user = session  #前端用

        client_env = ObjectDict({"name": self._client_env})
        self.namespace = {"client_env": client_env} #前端用

        # 内存优化
        self._wechat = None

        self.logger.debug("current_user:{}".format(self.current_user))
        self.logger.debug("+++++++++++++++++PREPARE OVER+++++++++++++++++++++")

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
