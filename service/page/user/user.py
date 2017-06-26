# coding=utf-8

from datetime import datetime

import tornado.gen as gen

import conf.common as const

from service.page.base import PageService

from util.common import ObjectDict
from util.tool import http_tool, str_tool

from setting import settings

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
            yield self.user_settings_ds.create_user_settings({
                "user_id": user_id
            })

        raise gen.Return(user_id)

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
        ret = yield self.user_wx_user_ds.get_wxuser({
            "wechat_id": wechat_id,
            "openid":    openid
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_wxuser_sysuser_id_wechat_id(self, sysuser_id, wechat_id):
        """根据 sysuer_id 和 wechat_id 获取 wxuser"""
        ret = yield self.user_wx_user_ds.get_wxuser({
            "wechat_id":  wechat_id,
            "sysuser_id": sysuser_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_wxuser_unionid_wechat_id(self, unionid, wechat_id, fields=None):
        """根据 unionid 和 wechat_id 获取 wxuser"""
        ret = yield self.user_wx_user_ds.get_wxuser({
            "wechat_id": wechat_id,
            "unionid":   unionid
        }, fields=fields)
        raise gen.Return(ret)

    @gen.coroutine
    def get_wxuser_id(self, wxuser_id):
        """根据 id 获取 wxuser """
        ret = yield self.user_wx_user_ds.get_wxuser({
            "id": wxuser_id
        })
        raise gen.Return(ret)

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

        qx_wxuser = yield self.get_wxuser_openid_wechat_id(
            openid=openid, wechat_id=qx_wechat_id)

        # 如果 qx_wxuser.sysuser_id = 0 表示只关注过，但是没有打开过页面
        if qx_wxuser and (qx_wxuser.sysuser_id == 0 or qx_wxuser.sysuser_id == user_id):
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

            # 如果获取到了 unionid，将所有该 unionid 的 wxuser 的 sysuser_id 设置为当前用户 id
            if userinfo.unionid:
                yield self.user_wx_user_ds.update_wxuser(
                    conds={"unionid": userinfo.unionid},
                    fields={"sysuser_id": user_id}
                )
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
    def get_valid_employee_by_user_id(self, user_id, company_id):
        ret = yield self.user_employee_ds.get_employee({
            "sysuser_id": user_id,
            "disable":    const.OLD_YES,
            "activation": const.OLD_YES,
            "company_id": company_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_employee_total_points(self, employee_id):
        """获取员工总积分"""
        employee_sum = yield self.user_employee_points_record_ds.get_user_employee_points_record_sum(
            conds={ "employee_id": employee_id }, fields=["award"])

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
            conds={ "wxuser_id": qx_wxuserid },
            fields=['amount'],
            appends=[" and hb_config_id in %s" % str_tool.set_literl(hb_config_ids)]
        )

        return hb_items_sum.sum_amount if hb_items_sum.sum_amount else 0

    @gen.coroutine
    def get_employee_cert_conf(self, company_id):
        ret = yield self.hr_employee_cert_conf_ds.get_employee_cert_conf({
            "company_id": company_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_employee_by_id(self, employee_id):
        ret = yield self.user_employee_ds.get_employee({
            "id": employee_id
        })
        return ret

    @gen.coroutine
    def update_user(self, user_id, **kwargs):
        kwargs = ObjectDict(kwargs)
        fields = {}
        if kwargs.email:
            fields.update(email=str(kwargs.email))
        if kwargs.mobile:
            fields.update(mobile=int(kwargs.mobile))
        if kwargs.name:
            fields.update(name=str(kwargs.name))
        self.logger.debug(fields)

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
    def employee_add_reward(self,
                            employee_id,
                            company_id,
                            position_id,
                            berecom_user_id,
                            award_type=const.EMPLOYEE_AWARD_TYPE_DEFAULT_ERROR,
                            **kw):
        """给员工添加积分的公共方法
        所有给员工添加积分的动作，都要走这个方法！
        """

        # 校验 award_type:
        if award_type == const.EMPLOYEE_AWARD_TYPE_DEFAULT_ERROR:
            self.logger.warn("award_type is not specified, return")
            return

        if award_type == const.EMPLOYEE_AWARD_TYPE_SHARE_APPLY and not kw.get('application_id'):
            self.logger.warn("application_id not specified, return")
            return

        # 校验员工
        employee = yield self.user_employee_ds.get_employee({
            'id':         employee_id,
            'activation': const.OLD_YES,
            'disable':    const.OLD_YES
        })
        if not employee:
            return

        # 获取积分模版对应的所需增加积分数 award_points
        type_templateid_mapping = {
            const.EMPLOYEE_AWARD_TYPE_SHARE_CLICK:
                const.RECRUIT_STATUS_RECOMCLICK_ID,

            const.EMPLOYEE_AWARD_TYPE_SHARE_APPLY:
                const.RECRUIT_STATUS_APPLY_ID,

            const.EMPLOYEE_AWARD_TYPE_RECOM:
                const.RECRUIT_STATUS_FULL_RECOM_INFO_ID
        }

        template_id = type_templateid_mapping.get(award_type)
        if not template_id:
            raise ValueError("invalid employee_award_type: %s" % award_type)

        points_conf = yield self.hr_points_conf_ds.get_points_conf(
            conds={"company_id":  company_id, "template_id": template_id },
            appends=["ORDER BY id DESC", "LIMIT 1"]
        )
        award_points = points_conf.reward

        # 插入积分数据 user_employee_points_record
        fields = {
            "employee_id":       employee_id,
            "application_id":    kw['application_id'] if award_type == const.EMPLOYEE_AWARD_TYPE_SHARE_APPLY else 0,
            "reason":            points_conf.status_name,
            "award":             award_points,
            "position_id":       position_id,
            "award_config_id":   points_conf.id,
            "recom_wxuser":      employee.wxuser_id,
            "recom_user_id":     employee.sysuser_id,
            "berecom_user_id":   berecom_user_id
        }

        yield self.user_employee_points_record_ds.create_user_employee_points_record(
            fields=fields
        )

        # 修改 user_employee.award
        yield self.user_employee_ds.update_employee(
            conds={'id': employee_id},
            fields={'award': int(employee.award + award_points)}
        )
        return

    @gen.coroutine
    def add_user_viewed_position(self, user_id, position_id):
        """
        添加用户已阅读职位，Gamma 使用
        :param user_id:
        :param position_id:
        :return:
        """

        if not user_id or not position_id:
            return False

        ret = yield self.thrift_searchcondition_ds.add_user_viewed_position(user_id, position_id)
        return ret
