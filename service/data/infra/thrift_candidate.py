# coding=utf-8

import tornado.gen as gen

from service.data.base import DataService
from service.data.infra.framework.client.client import ServiceClientFactory
from thrift_gen.gen.candidate.service.CandidateService import Client as CandidateServiceClient
from thrift_gen.gen.candidate.struct.ttypes import CandidateListParam, RecommmendParam
from thrift_gen.gen.common.struct.ttypes import BIZException
from util.common import ObjectDict
import conf.common as const


class ThriftCandidateDataService(DataService):

    """对接 CandidateService 的 thrift 接口
    """

    candidate_service_cilent = ServiceClientFactory.get_service(
        CandidateServiceClient)

    @gen.coroutine
    def send_candidate_view_position(self, user_id, position_id, sharechain_id):
        """刷新候选人链路信息，调用基础服务"""

        self.logger.debug("[thfirt] send_candidate_view_position params: %s" % dict(
            user_id=user_id, position_id=position_id, sharechain_id=sharechain_id))

        ret = None
        try:
            ret = yield self.candidate_service_cilent.glancePosition(
                int(user_id), int(position_id), int(sharechain_id))
        except:
            pass
        finally:
            return ret

    @gen.coroutine
    def send_candidate_interested(self, user_id, position_id, is_interested):
        """刷新候选人感兴趣，调用基础服务"""

        self.logger.debug(
            "[thfirt] send_candidate_interested params: %s" % dict(
                user_id=user_id, position_id=position_id, is_interested=is_interested))

        ret = yield self.candidate_service_cilent.changeInteresting(int(user_id), int(position_id), int(is_interested))
        raise gen.Return(ret)

    @gen.coroutine
    def get_candidate_list(self, post_user_id, click_time, is_recom, company_id):
        """获取候选人（要推荐的人）列表"""

        self.logger.debug("[thfirt] get_candidate_list params: %s" % dict(
            post_user_id=post_user_id, click_time=click_time, is_recom=is_recom, company_id=company_id))

        params = CandidateListParam()
        params.postUserId = int(post_user_id)
        params.clickTime = str(click_time)
        params.recoms = is_recom  # -> [int]
        params.companyId = int(company_id)

        ret = []
        try:
            ret_list = yield self.candidate_service_cilent.candidateList(params)
        except BIZException as BizE:
            self.logger.warn("%s - %s" % (BizE.code, BizE.message))
        else:
            self.logger.debug("[thrift] get_candidate_list: %s" % ret_list)

            for el in ret_list:
                recom_group = ObjectDict()
                recom_group.position_id = el.positionId
                recom_group.position_name = el.positionName
                recom_group.candidates = []

                for c in el.candidates:
                    c_info = ObjectDict()
                    c_info.id = c.id
                    c_info.presentee_user_id = c.presenteeUserId          # 被动求职者编号
                    c_info.presentee_name = c.presenteeName               # 被动求职者称呼
                    c_info.presentee_friend_id = c.presenteeFriendId      # 一度朋友编号
                    c_info.presentee_friend_name = c.presenteeFriendName  # 一度朋友称呼
                    c_info.presentee_logo = c.presenteeLogo               # 头像
                    c_info.is_recom = c.isRecom                           # 推荐状态
                    c_info.is_interested = const.YES if c.insterested else const.NO
                    c_info.view_number = c.viewNumber
                    recom_group.candidates.append(c_info)

                ret.append(recom_group)
        return ret

    @gen.coroutine
    def recommend(self, post_user_id, click_time, recom_record_id, realname, company,
                  position, mobile, recom_reason, company_id, gender, email):
        """ POST 推荐， 返回 recommend_result

        candidate_struct.RecommendResult recommend(
            1: candidate_struct.RecommmendParam  param
        ) throws(1: common_struct.BIZException  e)

        """

        self.logger.debug("[thfirt] recommend params: %s" % dict(
            post_user_id=post_user_id, click_time=click_time, recom_record_id=recom_record_id, realname=realname,
            company=company, position=position, mobile=mobile, recom_reason=recom_reason, company_id=company_id,
            gender=gender, email=email))

        recom_params = RecommmendParam()

        recom_params.id = int(recom_record_id)
        recom_params.realName = str(realname)
        recom_params.company = str(company)
        recom_params.position = str(position)
        recom_params.mobile = str(mobile)
        recom_params.recomReason = str(recom_reason)
        recom_params.companyId = int(company_id)
        recom_params.postUserId = int(post_user_id)
        recom_params.clickTime = str(click_time)
        recom_params.gender = int(gender)
        recom_params.email = str(email)


        try:
            recommend_result = yield self.candidate_service_cilent.recommend(
                recom_params)
            self.logger.debug("[recommend_result]: %s" % recommend_result)

        except BIZException as BizE:
            self.logger.warn("%s - %s" % (BizE.code, BizE.message))
            raise BizE

        return recommend_result

    @gen.coroutine
    def get_recommendations(self, company_id, list_of_recom_ids):

        self.logger.debug("[thfirt] get_recommendations params: %s" % dict(company_id=company_id, list_of_recom_ids=list_of_recom_ids))

        try:
            recom_result = yield self.candidate_service_cilent.getRecomendations(
                int(company_id), list_of_recom_ids)

        except BIZException as BizE:
            self.logger.warn("%s - %s" % (BizE.code, BizE.message))
            raise BizE

        return recom_result

    @gen.coroutine
    def get_recommendation(self, recom_id, post_user_id):

        self.logger.debug("[thfirt] get_recommendation params: %s" % dict(recom_id=recom_id, post_user_id=post_user_id))

        try:
            recom_record_result = yield self.candidate_service_cilent.getRecommendation(
                int(recom_id), int(post_user_id))

        except BIZException as BizE:
            self.logger.warn("%s - %s" % (BizE.code, BizE.message))
            raise BizE

        return recom_record_result

    @gen.coroutine
    def ignore(self, id, company_id, post_user_id,  click_time):

        self.logger.debug("[thfirt] ignore params: %s" % dict(id=id, company_id=company_id, post_user_id=post_user_id, click_time=click_time))

        try:
            recommend_result = yield self.candidate_service_cilent.ignore(
                int(id), int(company_id), int(post_user_id), str(click_time))
        except BIZException as BizE:
            self.logger.warn("%s - %s" % (BizE.code, BizE.message))
            return None
        else:
            return recommend_result

    @gen.coroutine
    def sort(self, post_user_id, company_id):

        self.logger.debug("[thfirt] sort params: %s" % dict(post_user_id=post_user_id, company_id=company_id))

        try:
            sort_result = yield self.candidate_service_cilent.getRecommendatorySorting(
                int(post_user_id), int(company_id))

        except BIZException as BizE:
            self.logger.warn("%s - %s" % (BizE.code, BizE.message))
            return None
        else:
            return sort_result
