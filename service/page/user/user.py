# coding=utf-8

from datetime import datetime

import tornado.gen as gen

import conf.common as const

from service.page.base import PageService

from util.common import ObjectDict
from util.tool import http_tool, str_tool, url_tool

from setting import settings
from util.common.decorator import log_time
import time


class UserPageService(PageService):
    def __init__(self):
        super().__init__()

    @gen.coroutine
    def create_user_user(self, userinfo, wechat_id, remote_ip, source):
        """
        根据微信授权得到的 userinfo 创建 user_user
        :param userinfo:
        :param wechat_id:
        :param remote_ip:
        :param source:
        """
        # 查询 这个 unionid 是不是已经存在
        user_record = yield self.user_user_ds.get_user({
            "unionid":  userinfo.unionid,
            "parentid": 0  # 保证查找正常的 user record
        })

        # 如果存在，返回 userid
        if user_record:
            user_id = user_record.id
        else:
            # 如果不存在，创建 user_user 记录，返回 user_id
            user_id = yield self.user_user_ds.create_user({
                "username":         userinfo.unionid,
                "country_code":     "",
                "password":         "",
                "register_time":    datetime.now(),
                "register_ip":      remote_ip,
                "mobile":           0,
                "national_code_id": 1,
                "wechat_id":        wechat_id,
                "last_login_time":  datetime.now(),
                "last_login_ip":    remote_ip,
                "login_count":      1,
                "unionid":          userinfo.unionid,
                "source":           source,
                "nickname":         '匿名用户' if userinfo.nickname == '(未知)' else userinfo.nickname,
                "name":             "",
                "headimg":          userinfo.headimgurl,
            })

            assert user_id
            yield self.infra_privacy_ds.insert_privacy_record(user_id)
            yield self.user_settings_ds.create_user_settings({
                "user_id": user_id
            })

        raise gen.Return(user_id)

    @log_time
    @gen.coroutine
    def get_user_user(self, params):
        """
        根据参数，查找 user_user
        Usage:
            get_user_user({
                'id': id,
                'unionid': unionid,
                'mobile': mobile
            })
        :param params:
        :return: dict()
        """

        ret = yield self.user_user_ds.get_user(params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_wxuser_openid_wechat_id(self, openid, wechat_id):
        """根据 openid 和 wechat_id 获取 wxuser"""
        ret = yield self.user_wx_user_ds.get_wxuser(conds={
            "wechat_id": wechat_id,
            "openid":    openid
        })
        raise gen.Return(ret)

    @log_time
    @gen.coroutine
    def get_wxuser_sysuser_id_wechat_id(self, sysuser_id, wechat_id):
        """根据 sysuer_id 和 wechat_id 获取 wxuser"""
        ret = yield self.user_wx_user_ds.get_wxuser(conds={
            "wechat_id":  wechat_id,
            "sysuser_id": sysuser_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_wxuser_unionid_wechat_id(self, unionid, wechat_id, fields=None):
        """根据 unionid 和 wechat_id 获取 wxuser"""
        ret = yield self.user_wx_user_ds.get_wxuser(conds={
            "wechat_id": wechat_id,
            "unionid":   unionid
        }, fields=fields)
        raise gen.Return(ret)

    @gen.coroutine
    def get_wxuser_id(self, wxuser_id):
        """根据 id 获取 wxuser """
        ret = yield self.user_wx_user_ds.get_wxuser(conds={
            "id": wxuser_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def set_wxuser_is_subscribe(self, wxuser):
        ret = yield self.user_wx_user_ds.update_wxuser(
            conds={'id': wxuser.id}, fields={'is_subscribe': const.YES})
        return ret

    @gen.coroutine
    def create_user_wx_user_ent(self, openid, unionid, wechat_id):
        """根据 unionid 创建 企业号微信用户信息"""

        wxuser = yield self.get_wxuser_openid_wechat_id(
            openid=openid, wechat_id=wechat_id)
        qx_wxuser = yield self.get_wxuser_unionid_wechat_id(
            unionid=unionid, wechat_id=settings['qx_wechat_id'])

        if wxuser:
            wxuser_id = wxuser.id
            yield self.user_wx_user_ds.update_wxuser(
                conds={
                    "id": wxuser.id
                },
                fields={
                    "is_subscribe": wxuser.is_subscribe or 0,
                    "sysuser_id":   qx_wxuser.sysuser_id,
                    "openid":       openid,
                    "nickname":     qx_wxuser.nickname,
                    "sex":          qx_wxuser.sex or 0,
                    "city":         qx_wxuser.city,
                    "country":      qx_wxuser.country,
                    "province":     qx_wxuser.province,
                    "language":     qx_wxuser.language,
                    "headimgurl":   qx_wxuser.headimgurl,
                    "wechat_id":    wechat_id,
                    "unionid":      qx_wxuser.unionid,
                    "source":       const.WX_USER_SOURCE_OAUTH_UPDATE
                })

        else:
            wxuser_id = yield self.user_wx_user_ds.create_wxuser({
                "is_subscribe": 0,
                "sysuser_id":   qx_wxuser.sysuser_id,
                "openid":       openid,
                "nickname":     qx_wxuser.nickname,
                "sex":          qx_wxuser.sex or 0,
                "city":         qx_wxuser.city,
                "country":      qx_wxuser.country,
                "province":     qx_wxuser.province,
                "language":     qx_wxuser.language,
                "headimgurl":   qx_wxuser.headimgurl,
                "wechat_id":    wechat_id,
                "unionid":      qx_wxuser.unionid,
                "source":       const.WX_USER_SOURCE_OAUTH
            })

        wxuser = yield self.get_wxuser_id(wxuser_id=wxuser_id)
        raise gen.Return(wxuser)

    @gen.coroutine
    def create_qx_wxuser_by_userinfo(self, userinfo, user_id):
        """从微信授权的 userinfo 创建 qx user"""
        qx_wechat_id = settings['qx_wechat_id']
        openid = userinfo.openid

        # 如果获取到了 unionid，将所有该 unionid 的 wxuser 的 sysuser_id 设置为当前用户 id
        if userinfo.unionid:
            yield self.user_wx_user_ds.update_wxuser(
                conds={"unionid": userinfo.unionid},
                fields={"sysuser_id": user_id}
            )

        qx_wxuser = yield self.get_wxuser_openid_wechat_id(
            openid=openid, wechat_id=qx_wechat_id)

        # 如果 qx_wxuser.sysuser_id = 0 表示只关注过，但是没有打开过页面
        if qx_wxuser:
            yield self.user_wx_user_ds.update_wxuser(
                conds={"id": qx_wxuser.id},
                fields={
                    "sysuser_id": user_id,
                    "openid":     userinfo.openid,
                    "nickname":   userinfo.nickname,
                    "sex":        userinfo.sex or 0,
                    "city":       userinfo.city,
                    "country":    userinfo.country,
                    "province":   userinfo.province,
                    "language":   userinfo.language,
                    "headimgurl": userinfo.headimgurl,
                    "unionid":    userinfo.unionid if userinfo.unionid else "",
                    "source":     const.WX_USER_SOURCE_OAUTH_UPDATE
                })

        else:
            yield self.user_wx_user_ds.create_wxuser({
                "is_subscribe": 0,
                "sysuser_id":   user_id,
                "openid":       userinfo.openid,
                "nickname":     userinfo.nickname,
                "sex":          userinfo.sex or 0,
                "city":         userinfo.city,
                "country":      userinfo.country,
                "province":     userinfo.province,
                "language":     userinfo.language,
                "headimgurl":   userinfo.headimgurl,
                "wechat_id":    qx_wechat_id,
                "unionid":      userinfo.unionid if userinfo.unionid else "",
                "source":       const.WX_USER_SOURCE_OAUTH
            })

    @gen.coroutine
    def ensure_user_unionid(self, user_id, unionid):
        user = yield self.user_user_ds.get_user(
            conds={'id': user_id},
            fields=['unionid']
        )
        if user.unionid != unionid:
            self.logger.warning("user_user.unionid incorrect, user:{}, real_unionid: {}".format(user, unionid))
            yield self.user_user_ds.update_user(
                conds={'id': user_id},
                fields={'unionid': unionid}
            )
            self.logger.warning("fixed")

    @gen.coroutine
    def update_user_user_current_info(self, sysuser_id, data):
        """更新用户真实姓名，最近工作单位和最近职位"""
        response = yield self.user_user_ds.update_user(
            conds={'id': sysuser_id},
            fields={
                'name':     data.name,
                'company':  data.company,
                'position': data.position
            })
        raise gen.Return(response)

    @gen.coroutine
    def bind_mobile_password(self, user_id, mobile, password):
        """用户手机号绑定操作，更新 username, mobile, password"""
        yield self.user_user_ds.update_user(
            conds={
                'id': user_id
            },
            fields={
                'mobile':   int(mobile),
                'username': str(mobile),
                'password': password,
            })

    @gen.coroutine
    def update_user_wx_info(self, unionid, userinfo):
        """更新用户的user_user中微信相关的信息"""
        yield self.user_user_ds.update_user(
            conds={
                'unionid': unionid
            },
            fields={
                "nickname": userinfo.nickname,
                "headimg": userinfo.headimgurl
            })

    @gen.coroutine
    def update_wxuser_wx_info(self, unionid, userinfo):
        """
        更新老微信 wxuser 信息
        :param unionid:
        :param userinfo:
        :return:
        """
        yield self.user_wx_user_ds.update_wxuser(
            conds={"unionid": unionid,
                   "wechat_id": settings['qx_wechat_id']},
            fields={
                "nickname": userinfo.nickname,
                "sex": userinfo.sex or 0,
                "city": userinfo.city,
                "country": userinfo.country,
                "province": userinfo.province,
                "headimgurl": userinfo.headimgurl
            })

    @gen.coroutine
    def get_valid_employee_by_user_id(self, user_id, company_id):
        """ 根据 user_id, company_id 找到合法的员工数据

        在 company_id 属于集团公司时，
        获取到的员工的 company_id 属性可能和参数中的 company_id 不同
        此时员工数据会带着 group_company_id 属性
        :param user_id: 当前用户id
        :param company_id: 当前公众号的 company_id
        """

        check_group_passed = yield self.infra_user_ds.is_valid_employee(
            user_id, company_id)

        if not check_group_passed:
            return ObjectDict()

        ret = yield self.user_employee_ds.get_employee(
            conds={
                "sysuser_id": user_id,
                "disable":    const.OLD_YES,
                "activation": const.OLD_YES
            })

        # 可能查到多条关系记录，但是他们的 group_company_id 应该是一样的
        # 在此不做过多校验
        if ret and ret.company_id != company_id:
            group_company_rel = yield self.hr_group_company_rel_ds.get_hr_group_company_rel(
                conds={"company_id": company_id}
            )

            ret.group_company_id = group_company_rel.group_id

        return ret

    @gen.coroutine
    def get_employee_total_points(self, employee_id):
        """获取员工总积分"""
        employee_sum = yield self.user_employee_points_record_ds.get_user_employee_points_record_sum(
            conds={"employee_id": employee_id}, fields=["award"])

        # 查询sum的SQL可能返回None，这里做下校验
        if employee_sum is None:
            return 0
        if employee_sum.sum_award:
            return employee_sum.sum_award
        return 0

    @gen.coroutine
    def get_employee_recommend_hb_amount(self, company_id, qx_wxuserid):
        """
        获取在在公司下单个 qx_openid 获取的推荐红包金额总额
        :param company_id:
        :param qx_wxuserid:
        :return:
        """
        hb_config_list = yield self.hr_hb_config_ds.get_hr_hb_config_list({
            'company_id': company_id,
            'type': 1
        })

        if not hb_config_list:
            return 0

        hb_config_ids = [e.id for e in hb_config_list]

        hb_items_sum = yield self.hr_hb_items_ds.get_hb_items_amount_sum(
            conds={"wxuser_id": qx_wxuserid},
            fields=['amount'],
            appends=[" and hb_config_id in %s" % str_tool.set_literl(hb_config_ids)]
        )
        if hb_items_sum is None:
            return 0

        return hb_items_sum.sum_amount if hb_items_sum.sum_amount else 0

    @gen.coroutine
    def get_employee_cert_conf(self, company_id):
        ret = yield self.hr_employee_cert_conf_ds.get_employee_cert_conf({
            "company_id": company_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def update_user(self, user_id, escape_mobile=False, **kwargs):
        kwargs = ObjectDict(kwargs)
        fields = {}
        if 'email' in kwargs:
            fields.update(email=str(kwargs.email))

        if not escape_mobile and 'mobile' in kwargs:
            country_code, phone_number = str_tool.split_phone_number(str(kwargs.mobile))
            fields.update(mobile=int(phone_number))
            fields.update(country_code=country_code)

        if 'name' in kwargs:
            fields.update(name=str(kwargs.name))

        ret = 0
        if fields:
            ret = yield self.user_user_ds.update_user(
                conds={"id": user_id}, fields=fields)
        return ret

    @gen.coroutine
    def get_hr_info_by_mobile(self, mobile):
        """获取 hr 信息"""
        hr_account = yield self.user_hr_account_ds.get_hr_account({
            "mobile": mobile
        })

        raise gen.Return(hr_account)

    @gen.coroutine
    def get_employee_by_id(self, employee_id):
        """获取user_employee"""
        employee = yield self.user_employee_ds.get_employee(
            {'id': employee_id})

        raise gen.Return(employee)

    @gen.coroutine
    def favorite_position(self, user_id, position_id):
        """用户收藏职位的粒子操作
        :param user_id: user_id
        :param pid: 职位id
        """

        ret = yield \
            self.thrift_searchcondition_ds.create_collect_position(user_id, position_id)
        raise gen.Return(ret.status)

    @gen.coroutine
    def favorite_referral_position(self, user_id, employee_id, position_id, psc):
        """用户收藏员工推荐的职位的粒子操作
        :param user_id: user_id
        :param employee_id: 员工编号
        :param position_id: 职位id
        :param psc: 分享链路
        """
        params = {
            "user_id": user_id,
            "position_id": position_id,
            "employee_id": employee_id,
            "psc": psc
        }
        ret = yield self.infra_user_ds.infra_create_collect_position(params)
        raise gen.Return(ret.data.status)

    @gen.coroutine
    def unfavorite_position(self, user_id, position_id):
        """用户取消收藏职位的粒子操作
        :param user_id: user_id
        :param pid: 职位id
        """
        ret = yield \
            self.thrift_searchcondition_ds.delete_collect_position(user_id, position_id)
        raise gen.Return(ret.status)

    @gen.coroutine
    def add_user_fav_position(self, position_id, user_id, favorite, mobile, recom_user_id):
        """
        增加用户感兴趣记录
        :param position_id:
        :param user_id:
        :param favorite: 2:感兴趣
        :param mobile:
        :param recom_user_id:
        :return: (result, fav_id or None)
        """

        fav = yield self.user_fav_position_ds.get_user_fav_position({
            "position_id": position_id,
            "sysuser_id":  user_id,
            "favorite":    favorite,
        })

        if fav:
            yield self.user_fav_position_ds.update_user_fav_position(
                conds={"id": fav.id},
                fields={"mobile": fav.mobile or mobile}
            )
            return False, None

        else:
            fav_id = yield self.user_fav_position_ds.insert_user_fav_position(
                fields=ObjectDict(
                    sysuser_id=user_id,
                    position_id=position_id,
                    mobile=mobile,
                    favorite=favorite,
                    recom_user_id=recom_user_id
                ))
            return True, fav_id

    @gen.coroutine
    def get_redpacket_list(self, params):
        """
        获取红包列表
        :param params:
        :return:
        """
        ret = yield self.infra_user_ds.get_redpacket_list(params)
        if int(ret.code) == const.API_SUCCESS:
            data = ret.data
        else:
            data = ObjectDict()
        return data

    @gen.coroutine
    def get_bonus_list(self, user_id, params):
        """
        获取奖金列表
        :param user_id:
        :param params:
        :return:
        """
        ret = yield self.infra_user_ds.get_bonus_list(user_id, params)
        if ret.status == const.API_SUCCESS:
            data = ret.data
        else:
            data = ObjectDict()
        return data

    @gen.coroutine
    def claim_bonus(self, bonus_id):
        """
        领取奖金
        :param bonus_id:
        :return:
        """
        ret = yield self.infra_user_ds.claim_bonus(bonus_id)
        return ret

    @gen.coroutine
    def post_hr_register(self, params):
        """
        注册 HR 用户
        :param params:
        :return:
        """

        ret = yield self.user_hr_account_ds.insert_hr_account(params)
        raise gen.Return(ret)

    @gen.coroutine
    def create_user_setting(self, user_id, banner_url='', privacy_policy=0):

        res = yield self.infra_user_ds.create_user_setting(
            user_id, banner_url, privacy_policy)

        return http_tool.unboxing(res)

    @gen.coroutine
    def add_user_viewed_position(self, user_id, position_id):
        """ 添加用户已阅读职位，Gamma 使用 """

        if not user_id or not position_id:
            return False

        ret = yield self.thrift_searchcondition_ds.add_user_viewed_position(user_id, position_id)
        return ret

    @staticmethod
    def adjust_sysuser(sysuser):
        """此方法将 sysuser 修改成适合微信端使用的结构，
        以后可以转换成domain对象"""

        ret = sysuser

        ret.headimg = url_tool.make_static_url(ret.headimg or const.SYSUSER_HEADIMG)
        ret.mobileverified = bool(ret.username.isdigit())

        if ret.mobileverified:
            ret.mobile = int(ret.username)

        ret.mobile_display = ''
        if ret.mobile:
            ret.mobile_display = str(ret.mobile)

        if ret.country_code and ret.country_code != '86':
            ret.mobile_display = '+{}-{}'.format(ret.country_code, ret.mobile_display)

        return ret

    @gen.coroutine
    def get_popup_info(self, user_id, company_id, position_id):
        """
        获取候选人进入职位详情弹层数据
        :param user_id:
        :param company_id:
        :return:
        """
        ret = yield self.infra_user_ds.get_popup_info(user_id, company_id, position_id)
        return ret

    @gen.coroutine
    def close_popup_window(self, user_id, company_id, type):
        """
        候选人职位详情页面弹层关闭
        :param user_id:
        :param company_id:
        :param type: int 0 二维码弹层 1简历完善度弹层
        :return:
        """
        ret = yield self.infra_user_ds.close_popup_window(user_id, company_id, type)
        return ret

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
        ret = yield self.infra_user_ds.referral_confirm_submit(company_id, user_id, post_user_id, position_id, origin)
        return ret

    @gen.coroutine
    def referral_related_positions(self, user_id, position_id):
        """
        候选人联系内推完成页面推荐三个相关职位信息
        :param user_id:
        :param position_id:
        :return:
        """
        ret = yield self.infra_user_ds.referral_related_positions(user_id, position_id)
        return ret

    @gen.coroutine
    def if_referral_position(self, company_id, recom, psc, pid, click_user_id):
        """
        候选人打开转发的职位链接，根据链接中参数判断最初转发该职位的人是否是员工
        :param company_id:
        :param recom:
        :param psc:
        :param pid:
        :param click_user_id:
        :return:
        """
        ret = yield self.infra_user_ds.if_referral_position(company_id, recom, psc, pid, click_user_id)
        return ret

    @gen.coroutine
    def if_ever_seek_recommend(self, recom_user_id, psc, pid, company_id, click_user_id):
        ret = yield self.infra_user_ds.if_ever_seek_recommend(recom_user_id, psc, pid, company_id, click_user_id)
        return ret

    @gen.coroutine
    def get_user_by_joywok_info(self, joywok_user_info, company_id):
        """
        根据麦当劳APP授权获取的员工信息查找仟寻用户信息：
        :param joywok_user_info:
        :param company_id:
        :return:
        """

        params = ObjectDict({
            "email": joywok_user_info.email,
            "custom_field": joywok_user_info.other_account,
            "mobile": joywok_user_info.bindmobile or "",
            "company_id": company_id
        })
        ret = yield self.infra_user_ds.infra_get_user_by_joywok_info(params)
        return ret

    @gen.coroutine
    def auto_bind_employee_by_joywok_info(self, joywok_user_info, company_id, sysuser_id):
        """
        对joywok的用户做自动认证：
        :param joywok_user_info:
        :param company_id:
        :return:
        """

        params = ObjectDict({
            "user_id": sysuser_id,
            "email": joywok_user_info.email,
            "custom_field": joywok_user_info.other_account,
            "mobile": joywok_user_info.bindmobile,
            "company_id": company_id,
            "cname": joywok_user_info.name
        })
        ret = yield self.infra_user_ds.infra_auto_bind_employee(params)
        return ret

    @gen.coroutine
    def upload_file_server(self, file_data, file_name, sysuser_id, scene_id=1):
        """
        自定义简历模板：上传身份证组件
        :param
        :return fileId
        """
        ret = yield self.infra_user_ds.upload_file_server(
            file_data, file_name, sysuser_id, scene_id)
        return ret

    @gen.coroutine
    def get_custom_file(self, file_id, sysuser_id):
        """
        自定义简历模板：上传身份证组件
        :param
        :return fileId
        """
        ret = yield self.infra_user_ds.get_custom_file(
            file_id, sysuser_id)
        return ret
