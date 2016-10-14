# coding=utf-8

from urllib.parse import quote
from urllib.request import urlopen
import ujson
from setting import settings
import conf.common as constant


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


def get_openid_by_code(self, code, wechat_id):
    account = self.db.get("select id, appid, secret, signature, "
                          "third_oauth from hr_wx_wechat where id = %s",
                          wechat_id)

    self.LOG.debug("get_openid_by_code account : {0}, wechat_id : {1}".format(
        str(account), str(wechat_id)))

    # 第三方平台授权oauth
    if int(account.third_oauth) == 1:
        component_appid = conf.component_app_id
        component_access_token = json.loads(self.application.session_manager.redis.get('component_access_token'))
        url = (const.WX_THIRD_OAUTH_GET_ACCESS_TOKEN % (account.appid, code, component_appid, component_access_token.get('component_access_token')))
        self.LOG.debug(url)
    else:
        url = (const.WX_OAUTH_GET_ACCESS_TOKEN % (account.appid, account.secret, code))
    try:
        response = mdict(json.loads(urlopen(url).read()), default="")
        self.LOG.debug("=====GET OPENID BY CODE======:" + str(response))
    except:
        self.LOG.info("Code invalid " + str(url))
        # traceback.print_exc()
        return None

    if response.openid and response.access_token:
        return response
    else:
        # LOG.info : response
        return None


def get_userinfo_by_openid(self, response):
    if not response:
        return response
    try:
        url = ( const.WX_OAUTH_GET_USERINFO
                % (response.access_token, response.openid))
        userinfo = mdict(json.loads(urlopen(url).read()))
        self.LOG.debug("==============GET USERINFO BY OPENID==============" + str(userinfo))
        if userinfo.openid:
            # update or insert into wx_group_user
            # =================================================TO DO ===============================================

            # ======================================================================================================
            return userinfo
        else :
            # LOG.info("Have no access getting userinfo : "+str(response))
            return response
    except:
        # LOG.error : userinfo
        self.LOG.debug("get userinfo failed : %s" % traceback.format_exc())
        return response

def get_userinfo_by_code(self, code, wechat_id):
    info = get_userinfo_by_openid(self, get_openid_by_code(self, code, wechat_id))
    return info


def refresh_access_token(self, wechat_id, refresh_token):
    account = self.db.get("select id, appid, secret, signature from hr_wx_wechat where id = %s", wechat_id)
    url = const.WX_OAUTH_REFRESH_ACCESS_TOKEN % (account.appid, refresh_token)
    response=None
    try:
        response = mdict(json.loads(urlopen(url).read()))
    except:
        self.LOG.info("Refresh fail : "+str(response))
    self.LOG.info(response)
    return response


def check_access_token(response):
    url = const.WX_CHECK_ACCESS_TOKEN % (response.openid, response.access_token)
    try:
        responses = mdict(json.loads(urlopen(url).read()))
        if responses.errcode == 0:
            return True
    except:
        # LOG.error
        pass
    return False
