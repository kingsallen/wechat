# coding=utf-8

from tornado import gen
from service.page.base import PageService
from urllib2 import quote, urlopen
from setting import settings
import conf.common as constant


class WechatOauthPageService(PageService):

    @staticmethod
    def get_oauth_code(handler, redirect_url=None, target_wechat=None,
                       oauth_type=None):
        assert handler and target_wechat and redirect_url
        assert oauth_type in ['userinfo', 'base']

        handler.logger.debug("target_wechat: {0}".format(target_wechat))
        redirect_url = quote(redirect_url)
        state = 0

        # 第三方
        if int(target_wechat.third_oauth) == 1:
            component_appid = settings['component_app_id']
            oauth_url = constant.WX_THIRD_OAUTH_GET_CODE % (
                target_wechat.appid, redirect_url, oauth_type, state,
                component_appid)
        # 非第三方
        else:
            oauth_url = constant.WX_OAUTH_GET_CODE % (
                target_wechat.appid, redirect_url, oauth_type, state)

        handler.logger.debug("oauth_url: {0}".format(oauth_url))
        handler.redirect(oauth_url)
