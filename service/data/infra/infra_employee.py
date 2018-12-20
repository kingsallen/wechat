# coding=utf-8

import tornado.gen as gen

import conf.common as const
import conf.path as path
from service.data.base import DataService
from util.common import ObjectDict
from util.tool.http_tool import http_get, http_post, http_put, unboxing, http_delete, http_post_multipart_form
from requests.models import Request
from setting import settings
from globals import env


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
        url = "{0}/{1}".format(settings['infra'], path.UPLOAD_RECOM_PROFILE)
        # requests的包不支持中文名文件上传，因此file_name单独传个字段
        request = Request(data={
            "employee": employee_id,
            "appid": const.APPID[env],
            "file_name": file_name
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
    def referral_connections(self, recom_user_id, end_user_id, chain_id, pid, parent_id):
        """
        人脉连连看
        :param recom_user_id: 当前转发用户user_id
        :param end_user_id:   链路结束用户user_id
        :param chain_id:      人脉连连看 链路id
        :param pid:   职位id
        :param parent_id:  父级链路id
        :return:
        """
        params = ObjectDict({
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
    def referral_evaluation_page_info(self, post_user_id, referral_id):
        """
        员工推荐评价页面 候选人和职位信息获取
        :param post_user_id:  推荐的员工的user_id
        :param  referral_id: 联系内推编号
        :return:
        """
        params = ObjectDict({
            "post_user_id": post_user_id,
            "referral_id": referral_id
        })
        ret = yield http_get(path.INFRA_REFERRAL_EVALUATION_PAGE, params)
        return ret

