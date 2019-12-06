# coding=utf-8

import tornado.gen as gen

import conf.common as const
import conf.path as path

from service.data.base import DataService
from util.common import ObjectDict
from util.common.decorator import log_coro
from util.tool.http_tool import http_get, http_post, http_put, unboxing, http_get_v2, http_post_v2, http_put_v2, unboxing_v2, \
    unboxing_fetchone, http_post_multipart_form, _v2_async_http_post
from conf.newinfra_service_conf.service_info import user_service, application_service
from conf.newinfra_service_conf.user import user
from conf.newinfra_service_conf.application import application
from util.common.exception import InfraOperationError
from tornado.httputil import url_concat
from setting import settings

from requests.models import Request


class InfraUserDataService(DataService):
    """对接 User服务
    referer: http://39.96.43.140:11005/swagger-ui.html#!/C31471299922514326381211532550921475/getUserByIdUsingGET"""

    @gen.coroutine
    def get_user_by_user_id(self, user_id):
        """获得用户数据"""
        params = ObjectDict({
            'user_id': user_id,
        })

        ret = yield http_get_v2(user.INFRA_USER_INFO, user_service, params)
        raise gen.Return(unboxing_v2(ret)) or ObjectDict()

    # todo(refactor_undo referral)
    @gen.coroutine
    def get_my_info(self, user_id, params):
        """获得用户我的个人中心数据"""
        ret = yield http_get(path.INFRA_MY_INFO.format(user_id), params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_wx_pc_combine(self, country_code, mobile, unionid):
        """手机号和微信号绑定接口"""

        params = ObjectDict({
            'countryCode': str(country_code),
            'mobile': str(mobile),
            'unionid': str(unionid),
        })

        ret = yield http_post_v2(user.INFRA_USER_COMBINE, user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_send_valid_code(self, country_code, mobile, type):
        """Request basic service send valid code to target mobile
        :param country_code: 国家代码
        :param mobile: target mobile number
        :param type:
        :return:
        """
        params = ObjectDict({
            'countryCode': str(country_code),
            'mobile': str(mobile),
            'type': int(type)
        })
        ret = yield http_post_v2(user.INFRA_USER_VALID, user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_send_voice_code_for_register(self, mobile):
        """Request basic service send valid voice code to target mobile (only for register)
        :param mobile: target mobile number
        :return:
        """
        params = ObjectDict({
            'mobile': mobile
        })
        ret = yield http_post_v2(user.INFRA_USER_VOICE_VALID, user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_verify_mobile(self, country_code, mobile, code, type):
        """
        Send code submitted by user to basic service.
        :param country_code: 国家代码
        :param mobile: target mobile number
        :param code:
        :param type
        :return:
        """
        params = ObjectDict({
            'countryCode': str(country_code),
            'mobile': str(mobile),
            'code': str(code),
            'type': int(type),
        })

        ret = yield http_post_v2(user.INFRA_USER_VERIFY, user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_login(self, params):
        """用户登录
        微信 unionid, 或者 mobile+password, 或者mobile+code, 3选1
        :param params: mobile: 手机号|| password: 密码|| code: 手机验证码|| unionid: 微信
        """

        ret = yield http_post_v2(user.INFRA_USER_LOGIN, user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_logout(self, user_id):
        """用户登出
        :param user_id: 用户 id
        """
        params = ObjectDict(
            user_id=user_id
        )

        ret = yield http_post_v2(user.INFRA_USER_LOGOUT, user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_register(self, params):
        """用户注册 """

        ret = yield http_post_v2(user.INFRA_USER_MOBILE_REGISTER, user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_ismobileregistered(self, mobile, country_code=86):
        """判断手机号是否已经注册
        :param country_code: 国家号
        :param mobile: 手机号
        """
        params = ObjectDict(
            countryCode=str(country_code),
            mobile=str(mobile),
        )

        ret = yield http_post_v2(user.INFRA_USER_ISMOBILEREGISTERED, user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def put_user(self, params):
        """更新用户信息"""

        ret = yield http_put_v2(user.INFRA_USER_INFO, user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_resetpassword(self, country_code, mobile, password):
        """重置密码"""

        params = ObjectDict({
            "countryCode": country_code,
            "mobile": mobile,
            "password": password
        })

        ret = yield http_post_v2(user.INFRA_USER_RESETPASSWD, user_service, params)
        raise gen.Return(ret)

    # todo(refactor_undo)
    @gen.coroutine
    def post_scanresult(self, params):
        """
        设置二维码扫描结果
        :param params:
        :return:
        """

        ret = yield http_post(path.INFRA_WXUSER_QRCODE_SCANRESULT, params)
        raise gen.Return(ret)

    # todo(refactor_undo company服务)
    @gen.coroutine
    def post_hr_register(self, params):
        """HR用户注册
        :param params
        """

        ret = yield http_post(path.INFRA_HRUSER, params)
        raise gen.Return(ret)

    @log_coro
    # todo(refactor_undo employee)
    @gen.coroutine
    def is_valid_employee(self, user_id, company_id, timeout=30):
        params = {
            "userId": int(user_id),
            "companyId": int(company_id)
        }

        res = yield http_get(path.INFRA_USER_EMPLOYEE_CHECK, params, timeout=timeout)
        ret, data = unboxing(res)

        return data.result if ret else False

    # todo(refactor_undo employee)
    @gen.coroutine
    def get_employee_survey_info(self, sysuser_id, employee_id):
        params = {
            "id": employee_id,
            "sysuser_id": sysuser_id,
            'activation': const.OLD_YES,
            'disable': const.OLD_YES
        }
        res = yield http_get(path.INFRA_USER_EMPLOYEE, params)
        result, data = unboxing(res)
        if len(data) > 0:
            d = data[0]
        else:
            d = {}
        return result, d

    # todo(refactor_undo employee)
    @gen.coroutine
    def post_employee_survey_info(self, employee_id, survey):
        params = {
            "id": employee_id,
            "position": survey["position"],
            "team_id": survey["department"],
            "job_grade": survey["job_grade"],
            "city_code": survey["city_code"],
            "degree": survey["degree"]
        }
        res = yield http_put(path.INFRA_USER_EMPLOYEE, params)
        return res

    # todo(refactor_undo employee)
    @gen.coroutine
    def update_recommend(self, params, employee_id):
        res = yield http_post(path.UPDATE_RECOMMEND.format(employee_id), params)
        return res

    # todo(refactor_undo application)
    @gen.coroutine
    def get_applied_applications(self, user_id, company_id, page_no=1, page_size=50):
        params = ObjectDict({
            "user_id": user_id,
            "company_id": company_id,
            "page_no": page_no,
            "page_size": page_size
        })
        res = yield http_get_v2(application.NEWINFRA_APPLICATION_RECORD_LIST, application_service, params)
        return res

    @gen.coroutine
    def get_applied_progress(self, user_id, app_id):
        params = ObjectDict({
            "user_id": user_id,
            "app_id": app_id
        })
        res = yield http_get_v2(application.NEWINFRA_APPLICATION_RECORD_DETAIL, application_service, params)
        return res

    # todo(refactor_undo referral)
    @gen.coroutine
    def get_bonus_list(self, user_id, params):
        res = yield http_get(path.INFRA_USER_BONUS_LIST.format(user_id), params)
        return res

    # todo(refactor_undo referral)
    @gen.coroutine
    def claim_bonus(self, bonus_id):
        res = yield http_put(path.INFRA_USER_CLAIM_BONUS.format(bonus_id))
        return res

    # todo(refactor_undo referral)
    @gen.coroutine
    def get_popup_info(self, user_id, company_id, position_id):
        """
        候选人进入职位详情弹层数据接口
        :return:
        """
        params = ObjectDict({
            "user_id": user_id,
            "company_id": company_id,
            "position_id": position_id
        })
        ret = yield http_get(path.INFRA_REFERRAL_POPUP, params)
        return ret

    # todo(refactor_undo referral)
    @gen.coroutine
    def close_popup_window(self, user_id, company_id, type):
        """
        候选人职位详情弹层关闭
        :param user_id:
        :param company_id:
        :param type: int   0 二维码弹层 1 简历完善度弹层
        :return:
        """
        params = ObjectDict({
            "user_id": user_id,
            "company_id": company_id,
            "type": type
        })
        ret = yield http_put(path.INFRA_REFERRAL_CLOSE_POPUP_WINDOW, params)
        return ret

    # todo(refactor_undo referral)
    @gen.coroutine
    def referral_confirm_submit(self, company_id, user_id, post_user_id, position_id, origin):
        """
        候选人联系内推：简历预览页面确认提交
        :param company_id:
        :param user_id:  候选人id
        :param post_user_id: 最初转发职位的员工的user_id
        :param position_id:
        :param origin: 申请来源，1 转发，2 连连看
        :return:
        """
        params = ObjectDict({
            "company_id": company_id,
            "user_id": user_id,
            "post_user_id": post_user_id,
            "position_id": position_id,
            "origin": origin
        })
        ret = yield http_post(path.INFRA_REFERRAL_CONTACT_PUSH, params)
        return ret

    # todo(refactor_undo referral)
    @gen.coroutine
    def referral_related_positions(self, user_id, company_id):
        """
        候选人联系内推完成页面推荐三个相关职位信息
        :param user_id:
        :param company_id:
        :return:
        """
        params = ObjectDict({
            "user_id": user_id,
            "company_id": company_id
        })
        ret = yield http_get(path.INFRA_REFERRAL_RELATIVE_POSITIONS, params)
        return ret

    # todo(refactor_undo referral)
    @gen.coroutine
    def if_referral_position(self, company_id, recom, psc, pid, click_user_id):
        """
        候选人打开转发的职位链接，根据链接中参数判断最初转发该职位的人是否是员工
        :param company_id:
        :param recom:  直接转发人的user_id
        :param psc:   父级链路id   candidate_share_chain.id
        :param pid:
        :param click_user_id:
        :return:
        """
        params = ObjectDict({
            "company_id": company_id,
            "recom_user_id": recom,
            "parent_chain_id": psc if psc else 0,
            "pid": pid,
            "presentee_user_id": click_user_id
        })
        ret = yield http_post(path.INFRA_IF_EMPLOYEE_POS, params)
        return ret

    # todo(refactor_undo referral)
    @gen.coroutine
    def if_ever_seek_recommend(self, recom_user_id, psc, pid, company_id, click_user_id):
        """
        候选人打开职位链接, 判断之前是否已经点击过“帮我内推”并且完成简历填写确认提交
        :param recom_user_id:  直接转发人的user_id
        :param psc:   父级链路id   candidate_share_chain.id
        :param pid:
        :param company_id:
        :param click_user_id:
        :return:
        """
        params = ObjectDict({
            "recom_user_id": recom_user_id,
            "psc": psc,
            "position_id": pid,
            "company_id": company_id,
            "presentee_user_id": click_user_id
        })
        ret = yield http_get(path.INFRA_IF_SEEK_CHECK, params)
        return ret

    @gen.coroutine
    def infra_add_fav_position(self, params):
        """增加用户感兴趣记录"""
        ret = yield http_post_v2(user.INFRA_USER_FAV_POSITION, user_service, params)
        return ret

    @gen.coroutine
    def infra_get_fav_positions(self, params):
        """通过职位列表获取用户感兴趣的记录"""
        ret = yield http_post_v2(user.INFRA_USER_FAV_POSITIONS, user_service, params)
        return ret

    @gen.coroutine
    def infra_add_user_settings(self, params):
        """增加用户设置记录"""
        ret = yield http_post_v2(user.INFRA_USER_SETTINGS, user_service, params)
        return ret

    @gen.coroutine
    def infra_get_collect_positions(self, params):
        """查看用户收藏职位"""
        ret = yield http_get_v2(user.INFRA_USER_COLLECT_POSITIONS, user_service, params)
        return ret

    @gen.coroutine
    def infra_get_collect_position(self, params):
        """获取职位收藏状态"""
        ret = yield http_get_v2(user.INFRA_USER_COLLECT_POSITION, user_service, params)
        return ret

    @gen.coroutine
    def infra_create_collect_position(self, params):
        """增加收藏职位"""
        ret = yield http_post_v2(user.INFRA_USER_COLLECT_POSITION, user_service, params)
        return ret

    @gen.coroutine
    def infra_get_user_by_joywok_info(self, params):
        """
        根据麦当劳APP授权获取的员工信息查找仟寻微信用户，及员工在仟寻系统的认证状态:
        :param params:
        :return:
        """
        ret = yield http_get_v2(user.INFRA_GET_USER_BY_JOYWOK_USER_INFO, user_service, params)
        return ret

    @gen.coroutine
    def infra_auto_bind_employee(self, params):
        """
        对joywok的用户做自动认证:
        :param params:
        :return:
        """
        ret = yield http_post(path.INFRA_AUTO_BIND_EMPLOYEE, params)
        return ret

    @gen.coroutine
    def post_wx_change_mobile(self, country_code, mobile, user_id):
        """手机号和微信号绑定接口"""

        params = ObjectDict({
            'country_code': str(country_code),
            'mobile': str(mobile),
            'user_id': str(user_id)
        })

        ret = yield http_post_v2(user.INFRA_USER_CHANGE_MOBILE, user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def upload_file_server(self, file_data, file_name, sysuser_id, scene_id):
        """
        自定义简历模板：上传身份证组件
        :param params:
        :return:
        """
        url = "{0}/{1}{2}?appid={appid}&interfaceid={interfaceid}".format(
            settings['cloud'],
            user_service.service_name,
            user.INFRA_CUSTOM_FILE_UPLOAD,
            appid=user_service.appid,
            interfaceid=user_service.interfaceid
        )
        request = Request(data={
            "fileName": file_name,
            "sceneId": scene_id, # 场景值：1 身份证识别
            "userId": sysuser_id,
            "source": 1 # 来源： wechat上传:1 pc上传:2
        },
            files={
                "file": ("", file_data)
            },
            url=url,
            method="POST"
        )
        p = request.prepare()
        body = p.body
        headers = p.headers

        ret = yield http_post_multipart_form(url, body, headers=headers)
        if ret.code != const.NEWINFRA_API_SUCCESS:
            raise InfraOperationError(ret.message)
        raise gen.Return(ret.data)

    @gen.coroutine
    def get_custom_file(self, file_id, sysuser_id):
        """
        自定义简历模板：上传身份证组件
        :param params:
        :return:
        """
        params = ObjectDict({
            "fileId": file_id,
            "userId": sysuser_id,
            "appid": user_service.appid,
            "interfaceid": user_service.interfaceid
        })

        path = "{0}/{1}{2}".format(settings['cloud'], user_service.service_name, user.INFRA_GET_CUSTOM_FILE)
        route = url_concat(path, params)  # post请求参数写在url里面，不能写在body里面
        ret = yield _v2_async_http_post(route)
        if ret.code != const.NEWINFRA_API_SUCCESS:
            raise InfraOperationError(ret.message)
        raise gen.Return(ret.data)

    @gen.coroutine
    def infra_delete_collect_position(self, params):
        """增加取消职位收藏"""
        ret = yield http_post_v2(user.INFRA_USER_CANCEL_COLLECT_POSITION, user_service, params)
        return ret

    @gen.coroutine
    def infra_add_user_viewed_position(self, params):
        """增加用户职位浏览数"""
        ret = yield http_post_v2(user.INFRA_USER_ADD_VIEWED_POSITION, user_service, params)
        return ret

    @gen.coroutine
    def infra_get_user(self, params):
        """获取用户信息"""
        ret = yield http_post_v2(user.INFRA_USER_USER_INFO, user_service, params)
        return unboxing_fetchone(ret)

    @gen.coroutine
    def infra_get_wxuser(self, params):
        """获取用户微信信息"""
        ret = yield http_get_v2(user.INFRA_USER_WX_USER_INFO, user_service, params)
        return unboxing_v2(ret) or ObjectDict()

    @gen.coroutine
    def infra_user_register(self, params):
        """用户qx授权"""
        ret = yield http_post_v2(user.INFRA_USER_REGISTER, user_service, params)
        return ret

    @gen.coroutine
    def infra_update_user_user(self, params):
        """更新用户信息"""
        ret = yield http_post_v2(user.INFRA_USER_INFO, user_service, params)
        return ret

    @gen.coroutine
    def infra_bind_wxuser(self, params):
        """根据 unionid 创建 企业号微信用户信息"""
        ret = yield http_post_v2(user.INFRA_WXUSER_BIND, user_service, params)
        return ret

    @gen.coroutine
    def infra_update_wxuser(self, params):
        """更新用户wxuser数据"""
        ret = yield http_put_v2(user.INFRA_WX_USER_INFO, user_service, params)
        return unboxing_v2(ret)

    @gen.coroutine
    def infra_update_wxuser_by_unionid(self, params):
        """更新用户wxuser数据 by unionid"""
        ret = yield http_put_v2(user.INFRA_WX_USER_INFO_BY_UNIONID, user_service, params)
        return ret

    @gen.coroutine
    def infra_create_wxuser(self, params):
        """增加wxuser信息"""
        ret = yield http_post_v2(user.INFRA_WX_USER_INFO, user_service, params)
        return unboxing_v2(ret)

    @gen.coroutine
    def infra_subscribe(self, params):
        """用户关注"""
        ret = yield http_post_v2(user.INFRA_USER_SUBSCRIBE, user_service, params)
        return unboxing_v2(ret)

    @gen.coroutine
    def infra_unsubscribe(self, params):
        """用户取消关注"""
        ret = yield http_post_v2(user.INFRA_USER_UNSUBSCRIBE, user_service, params)
        return unboxing_v2(ret)
