# coding=utf-8

import tornado.gen as gen

import conf.common as const
import conf.path as path
from service.data.base import DataService
from util.common import ObjectDict
from util.tool.http_tool import http_get, http_post, unboxing, http_delete, http_post_multipart_form, http_get_v2, http_post_v2, http_put
from requests.models import Request
from setting import settings
from globals import env
from conf.newinfra_service_conf.service_info import employee_service, parsing_service
from conf.newinfra_service_conf.employee import employee
from conf.newinfra_service_conf.parsing import parsing


class InfraEmployeeDataService(DataService):
    """对接内推服务"""

    @gen.coroutine
    def get_referral_policy(self, company_id):
        params = ObjectDict({
            "company_id": company_id
        })
        ret = yield http_get(path.REFERRAL_POLICY, params)
        return unboxing(ret)

    @gen.coroutine
    def create_interest_policy_count(self, params):
        ret = yield http_post(path.INTEREST_REFERRAL_POLICY, params)
        return unboxing(ret)

    @gen.coroutine
    def get_mate_num(self, company_id):
        ret = yield http_get(path.MATE_NUM.format(company_id))
        return unboxing(ret)

    @gen.coroutine
    def get_unread_praise(self, employee_id):
        ret = yield http_get(path.UNREAD_PRAISE.format(employee_id))
        return unboxing(ret)

    @gen.coroutine
    def vote_prasie(self, employee_id, praise_employee_id):
        ret = yield http_post(path.VOTE_PRAISE.format(employee_id, praise_employee_id))
        return unboxing(ret)

    @gen.coroutine
    def cancel_prasie(self, employee_id, praise_employee_id):
        ret = yield http_delete(path.VOTE_PRAISE.format(employee_id, praise_employee_id))
        return unboxing(ret)

    @gen.coroutine
    def get_last_rank_info(self, employee_id, type):
        params = ObjectDict({
            "type": type
        })
        ret = yield http_get(path.LAST_RANK_INFO.format(employee_id), params)
        return unboxing(ret)

    @gen.coroutine
    def get_current_user_rank_info(self, employee_id, type):
        params = ObjectDict({
            "type": type
        })
        ret = yield http_get(path.USER_RANK_INFO.format(employee_id), params)
        return unboxing(ret)

    @gen.coroutine
    def get_award_ladder_type(self, company_id):
        ret = yield http_get(path.LADDER_TYPE.format(company_id))
        return unboxing(ret)

    @gen.coroutine
    def get_bind_reward(self, company_id):
        params = ObjectDict({
            "companyId": company_id
        })
        ret = yield http_get(path.BIND_REWARD, params)
        return unboxing(ret)

    @gen.coroutine
    def upload_recom_profile(self, file_name, file_data, employee_id):
        url = "{0}/{1}{2}?appid={appid}&interfaceid={interfaceid}".format(
            settings['cloud'],
            parsing_service.service_name,
            parsing.UPLOAD_RECOM_PROFILE,
            appid=parsing_service.appid,
            interfaceid=parsing_service.interfaceid
        )
        # requests的包不支持中文名文件上传，因此file_name单独传个字段
        request = Request(data={
            "employeeId": employee_id,
            "filename": file_name
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
        return ret

    @gen.coroutine
    def get_referral_info(self, id):
        ret = yield http_get(path.REFERRAL_INFO.format(id))
        return ret

    @gen.coroutine
    def update_referral_info(self, params):
        ret = yield http_post(path.INFRA_REFERRAL_CONFIRM, params)
        return ret

    @gen.coroutine
    def get_referral_position_info(self, employee_id, pid):
        params = ObjectDict({
            "position": pid
        })
        ret = yield http_get(path.REFERRAL_POSITION_INFO_EMPLOYEE.format(employee_id), params)
        return ret

    @gen.coroutine
    def update_referral_position(self, employee_id, pid):
        params = ObjectDict({
            "position": pid
        })
        ret = yield http_post(path.REFERRAL_POSITION_INFO_EMPLOYEE.format(employee_id), params)
        return ret

    @gen.coroutine
    def update_referral_crucial_info(self, employee_id, params):
        ret = yield http_post(path.INFRA_REFERRAL_CRUCIAL_INFO.format(employee_id), params)
        return ret

    @gen.coroutine
    def get_referral_qrcode(self, url, logo):
        params = ObjectDict({
            "url": url,
            "logo": logo
        })
        ret = yield http_post(path.REFERRAL_QRCODE, params)
        return ret

    @gen.coroutine
    def get_employee_by_user_id(self, user_id):
        ret = yield http_get(path.INFRA_USER_EMPLOYEE_REFERRAL.format(user_id))
        return ret

    @gen.coroutine
    def get_referral_cards(self, user_id, timestamp, page_number, page_size, company_id):
        """
        十分钟消息模板：卡片数据获取
        :param user_id:   转发职位的员工的user_id
        :param timestamp: 发送消息模板的时间
        :param page_number:
        :param page_size:
        :param company_id:
        :return:
        """
        params = ObjectDict({
            "user_id": user_id,
            "timestamp": timestamp,
            "page_number": page_number,
            "page_size": page_size,
            "company_id": company_id
        })
        ret = yield http_post(path.INFRA_REFERRAL_CARDS, params)
        return ret

    @gen.coroutine
    def pass_referral_card(self, pid, user_id, company_id, card_user_id, timestamp):
        """
        十分钟消息模板：我不熟悉
        :param pid:
        :param user_id:       转发职位的user_id
        :param card_user_id:  当前卡片的user_id
        :param timestamp:     发送消息模板的时间
        :return:
        """
        params = ObjectDict({
            "pid": pid,
            "user_id": user_id,
            "company_id": company_id,
            "end_user_id": card_user_id,
            "timestamp": timestamp,
        })
        ret = yield http_post(path.INFRA_REFERRAL_PASS_CARDS, params)
        return ret

    @gen.coroutine
    def invite_cards_user_apply(self, pid, user_id, company_id, card_user_id, timestamp):
        """
        十分钟消息模板： 邀请投递
        :param pid:
        :param user_id:
        :param company_id:
        :param card_user_id:
        :param timestamp:
        :return:
        """
        params = ObjectDict({
            "pid": pid,
            "user_id": user_id,
            "company_id": company_id,
            "end_user_id": card_user_id,
            "timestamp": timestamp,
        })
        ret = yield http_post(path.INFRA_REFERRAL_INVITE_CARDS, params)
        return ret

    @gen.coroutine
    def invite_cards_invited(self, user_id, candidate_user_id, pid, company_id, timestamp, state):
        """
        邀请投递候选人不在线时，员工点击“人脉连连看”或“转发邀请”时才算已处理过该候选人
        :param user_id:  员工的user_id
        :param candidate_user_id:  候选人的user_id
        :param pid:
        :param company_id:
        :return:
        """
        params = ObjectDict({
            "pid": pid,
            "user_id": user_id,
            "company_id": company_id,
            "end_user_id": candidate_user_id,
            "timestamp": timestamp,
            "state": state
        })
        ret = yield http_post(path.INFRA_REFERRAL_INVITE_CARDS_INVITED, params)
        return ret

    @gen.coroutine
    def referral_connections(self, company_id, recom_user_id, end_user_id, chain_id, pid, parent_id):
        """
        人脉连连看
        :param company_id:
        :param recom_user_id: 当前转发用户user_id
        :param end_user_id:   链路结束用户user_id
        :param chain_id:      人脉连连看 链路id
        :param pid:   职位id
        :param parent_id:  父级链路id
        :return:
        """
        params = ObjectDict({
            "company_id": company_id,
            "recom_user_id": recom_user_id,
            "next_user_id": end_user_id,
            "chain_id": chain_id,
            "pid": pid,
            "parent_id": parent_id
        })
        ret = yield http_post(path.INFRA_REFERRAL_CONNECTIONS, params)
        return ret

    @gen.coroutine
    def referral_contact_push(self, user_id, position_id):
        """
        联系内推页面获取员工姓名、头像及职位名
        :param user_id:  员工的user_id
        :param position_id:
        :return:
        """
        params = ObjectDict({
            "user_id": user_id,
            "position_id": position_id
        })
        ret = yield http_get(path.INFRA_REFERRAL_CONTACT_INFO, params)
        return ret

    @gen.coroutine
    def referral_save_evaluation(self, params):
        """
        联系内推：推荐评价信息保存
        :param params:
        :return:
        """
        ret = yield http_post(path.INFRA_REFERRAL_EVALUATION, params)
        return ret

    @gen.coroutine
    def nonreferral_save_evaluation(self, params):
        """
        不是点击“帮我内推”button， 而是直接投递之后在推荐进度列表中进行"评价Ta"
        :param params:
        :return:
        """
        ret = yield http_post(path.INFRA_NONREFERRAL_EVALUATION, params)
        return ret

    @gen.coroutine
    def referral_evaluation_page_info(self, company_id, post_user_id, referral_id):
        """
        员工推荐评价页面 候选人和职位信息获取
        :param company_id
        :param post_user_id:  推荐的员工的user_id
        :param  referral_id: 联系内推编号
        :return:
        """
        params = ObjectDict({
            "company_id": company_id,
            "post_user_id": post_user_id,
            "referral_id": referral_id
        })
        ret = yield http_get(path.INFRA_REFERRAL_EVALUATION_PAGE, params)
        return ret

    @gen.coroutine
    def get_referral_progress(self, params):
        """
        员工中心 推荐进度：获取进度列表数据
        :param params:
        :return:
        """
        ret = yield http_post(path.INFRA_REFERRAL_PROGRESS, params)
        return ret

    @gen.coroutine
    def get_referral_progress_keyword(self, params):
        """
        员工中心 推荐进度 按候选人姓名搜索
        :param params:
        :return:
        """
        ret = yield http_get(path.INFRA_REFERRAL_PROGRESS_KEYWORD, params)
        return ret

    @gen.coroutine
    def get_referral_progress_detail(self, apply_id, params):
        """
        员工中心 推荐进度：分享内推进度页面
        :param apply_id
        :param params:
        :return:
        """
        ret = yield http_get(path.INFRA_REFERRAL_PROGRESS_DETAIL.format(apply_id), params)
        return ret

    @gen.coroutine
    def get_radar_top_data(self, user_id, company_id):
        """
        获取雷达页面顶部 浏览记录和求推荐数据
        :param user_id: 员工的user_id
        :return:
        """
        params = {
            "user_id": user_id,
            "company_id": company_id
        }
        ret = yield http_get(path.INFRA_REFERRAL_RADAR_TOP, params)
        return ret

    @gen.coroutine
    def get_radar_data(self, user_id, page_size, page_num, company_id):
        """
        获取雷达页面人脉数据
        :param user_id
        :param page_size:
        :param page_num:
        :param company_id
        :return:
        """
        params = {
            "user_id": user_id,
            "page": page_num,
            "size": page_size,
            "company_id": company_id
        }
        ret = yield http_get(path.INFRA_REFERRAL_RADAR, params)
        return ret

    @gen.coroutine
    def radar_card_position(self, user_id, company_id, pos_title, order, page_num, page_size):
        """
        人脉雷达-分类统计卡-职位浏览
        :param user_id:
        :param company_id
        :param pos_title:  按职位名搜索
        :param order:  排序规则： time  depth  view
        :param page_num:
        :param page_size:
        :return:
        """
        params = {
            "user_id": user_id,
            "company_id": company_id,
            "position_title": pos_title,
            "order": order,
            "page": page_num,
            "size": page_size
        }
        ret = yield http_get(path.INFRA_REFERRAL_RADAR_CARD_POS, params)
        return ret

    @gen.coroutine
    def radar_card_seek_recom(self, user_id, company_id, page_num, page_size):
        """
        人脉雷达-分类统计卡-求推荐
        :param user_id:
        :param company_id:
        :param page_num:
        :param page_size:
        :return:
        """
        params = {
            "user_id": user_id,
            "company_id": company_id,
            "page": page_num,
            "size": page_size
        }
        ret = yield http_get(path.INFRA_REFERRAL_RADAR_CARD_RECOM, params)
        return ret

    @gen.coroutine
    def infra_get_employee_custom_info(self, params):
        """获取员工补填信息"""
        ret = yield http_get_v2(employee.NEWINFRA_EMPLOYEE_CUSTOM_INFO, employee_service, params)
        return ret

    @gen.coroutine
    def infra_get_employee_custom_field(self, params):
        """获取补填字段配置数据"""
        ret = yield http_get_v2(employee.NEWINFRA_EMPLOYEE_CUSTOM_FIELD, employee_service, params)
        return ret

    @gen.coroutine
    def infra_get_employee_supply_info_by_custom_field(self, params):
        """获取补填字段配置数据"""
        ret = yield http_get_v2(employee.NEWINFRA_EMPLOYEE_SUPPLY_INFO_BY_CUSTOM_FIELD, employee_service, params)
        return ret

    @gen.coroutine
    def infra_get_employee_auth_tips_info(self, params):
        """获取认证自定义显示数据"""
        ret = yield http_get_v2(employee.NEWINFRA_EMPLOYEE_AUTH_TIPS_INFO, employee_service, params)
        return ret

    @gen.coroutine
    def infra_get_bind_email_is_valid(self, params):
        """获取认证邮件是否有效"""
        ret = yield http_get_v2(employee.NEWINFRA_BIND_EMAIL_IS_VALID, employee_service, params)
        return ret

    @gen.coroutine
    def infra_resend_bind_email(self, params):
        """重新发送认证邮件"""
        ret = yield http_post(path.INFRA_RESEND_BIND_EMAIL, params)
        return ret

    @gen.coroutine
    def infra_update_employee_custom_supply_info(self, params):
        """更新员工补填信息"""
        ret = yield http_put(path.INFRA_EMPLOYEE_CUSTOM_INFO, params)
        return ret

    @gen.coroutine
    def infra_submit_employee_subscribe_preference(self, params):
        """提交员工订阅偏好的信息"""
        ret = yield http_post_v2(employee.NEWINFRA_EMPLOYEE_SUBSCRIBE_PREFERENCE, employee_service, params)
        return ret

    @gen.coroutine
    def get_employee_cert_config(self, company_id, hraccount_id):
        """获取企业认证配置信息"""
        params = {
            "companyId": company_id,
            "hraccountId": hraccount_id,
            "type": 3
        }
        ret = yield http_get(path.INFRA_GET_EMPLOYEE_CERT_CONFIG, params)
        return ret

    @gen.coroutine
    def get_switch_workwx(self, company_id):
        """
        企业微信-OMS开关
        :param params:
        :return:
        """
        ret = yield http_get(path.INFRA_OMS_SWITCH_WORKWX.format(company_id))
        return ret

    @gen.coroutine
    def get_employee_mobile_info(self, sysuser_id):
        """
        员工积分兑换回填手机号
        :param params:
        :return:
        """
        params = ObjectDict({
            "user_id": sysuser_id
        })
        ret = yield http_get(path.INFRA_GET_EMPLOYEE_MOBILE_INFO, params)
        raise gen.Return(ret.data.get("data"))
