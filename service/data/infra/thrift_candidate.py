# coding=utf-8

import tornado.gen as gen

from service.data.base import DataService
from service.data.infra.framework.client.client import ServiceClientFactory
from service.page.employee.candidate import RecomException
from thrift_gen.gen.candidate.service.CandidateService import Client as CandidateServiceClient
from thrift_gen.gen.candidate.struct.ttypes import CandidateListParam, RecommmendParam
from thrift_gen.gen.common.struct.ttypes import BIZException
from util.common import ObjectDict


class ThriftCandidateDataService(DataService):

    """对接 CandidateService 的 thrift 接口
    """

    candidate_service_cilent = ServiceClientFactory.get_service(
        CandidateServiceClient)

    @gen.coroutine
    def send_candidate_view_position(self, user_id, position_id, sharechain_id):
        """刷新候选人链路信息，调用基础服务"""

        ret = yield self.candidate_service_cilent.glancePosition(int(user_id), int(position_id), int(sharechain_id))
        self.logger.debug("[thrift]send_candidate_view_position: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def send_candidate_interested(self, user_id, position_id, is_interested):
        """刷新候选人感兴趣，调用基础服务"""

        ret = yield self.candidate_service_cilent.changeInteresting(int(user_id), int(position_id), int(is_interested))
        self.logger.debug("[thrift]send_candidate_interested: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def get_candidate_list(self, post_user_id, click_time, is_recom, company_id):
        """获取候选人（要推荐的人）列表"""

        params = CandidateListParam()
        params.postUserId = int(post_user_id)
        params.clickTime = str(click_time)
        params.recoms = is_recom  # -> [int]
        params.companyId = int(company_id)

        try:
            ret_list = yield self.candidate_service_cilent.candidateList(params)
            self.logger.debug("[thrift]get_candidate_list: %s" % ret_list)

            ret = []

            for el in ret_list:
                recom_group = ObjectDict()
                recom_group.position_id = el.positionId
                recom_group.position_title = el.positionName
                recom_group.candidates = []

                for c in el.candidates:
                    c_info = ObjectDict()
                    c_info.recom_record_id = c.id
                    c_info.presentee_user_id = c.presenteeUserId  # 被动求职者编号
                    c_info.presentee_name = c.presenteeName  # 被动求职者称呼
                    c_info.presentee_friend_id = c.presenteeFriendId  # 一度朋友编号
                    c_info.presentee_friend_name = c.presenteeFriendName  # 一度朋友称呼
                    c_info.presentee_logo = c.presenteeLogo  # 头像
                    c_info.is_recom = c.isRecom  # 推荐状态
                    c_info.is_interested = c.isInsterested
                    c_info.view_num = c.viewNumber
                    recom_group.candidates.append(c_info)

                ret.append(recom_group)

        except BIZException as BizE:

            self.logger.warn("%s - %s" % (BizE.code, BizE.message))
            e = RecomException()
            e.code = BizE.code
            e.message = BizE.message
            raise e

        return ret

    @gen.coroutine
    def recommend(self, post_user_id, click_time, recom_record_id, realname, company,
                  position, mobile, recom_reason, company_id):
        """ POST 推荐， 返回 recommend_result

        candidate_struct.RecommendResult recommend(
            1: candidate_struct.RecommmendParam  param
        ) throws(1: common_struct.BIZException  e)

        """

        recom_params = RecommmendParam()

        recom_params.postUserId = post_user_id
        recom_params.clickTime = click_time
        recom_params.id = recom_record_id
        recom_params.realName = realname
        recom_params.company = company
        recom_params.position = position
        recom_params.mobile = mobile
        recom_params.recomReason = recom_reason
        recom_params.companyId = company_id

        try:
            recommend_result = yield self.candidate_service_cilent.recommend(
                recom_params)

        except BIZException as BizE:

            self.logger.warn("%s - %s" % (BizE.code, BizE.message))
            e = RecomException()
            e.code = BizE.code
            e.message = BizE.message
            raise e

        return recommend_result

    @gen.coroutine
    def get_recommendations(self, company_id, list_of_recom_ids):
        try:
            recom_result = yield self.candidate_service_cilent.getRecomendations(
                int(company_id), list_of_recom_ids)

        except BIZException as BizE:

            self.logger.warn("%s - %s" % (BizE.code, BizE.message))
            e = RecomException()
            e.code = BizE.code
            e.message = BizE.message
            raise e

        return recom_result

    @gen.coroutine
    def get_recommendation(self, recom_id, post_user_id):
        try:
            recom_record_result = yield self.candidate_service_cilent.getRecommendation(
                int(recom_id), int(post_user_id))

        except BIZException as BizE:

            self.logger.warn("%s - %s" % (BizE.code, BizE.message))
            e = RecomException()
            e.code = BizE.code
            e.message = BizE.message
            raise e

        return recom_record_result

    @gen.coroutine
    def ignore(self, id, company_id, post_user_id,  click_time):

        try:
            recommend_result = yield self.candidate_service_cilent.ignore(
                id, company_id, post_user_id, click_time)

        except BIZException as BizE:

            self.logger.warn("%s - %s" % (BizE.code, BizE.message))
            e = RecomException()
            e.code = BizE.code
            e.message = BizE.message
            raise e

        return recommend_result

    @gen.coroutine
    def sort(self, post_user_id, company_id):
        try:
            sort_result = yield self.candidate_service_cilent.getRecommendatorySorting(
                post_user_id, company_id)

        except BIZException as BizE:

            self.logger.warn("%s - %s" % (BizE.code, BizE.message))
            e = RecomException()
            e.code = BizE.code
            e.message = BizE.message
            raise e

        return sort_result
