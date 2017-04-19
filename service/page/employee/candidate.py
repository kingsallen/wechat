# coding=utf-8

from tornado import gen
from service.page.base import PageService
from util.common import ObjectDict


class RecomException(Exception):
    __slots__ = ['code', 'message']


class CandidatePageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def send_candidate_view_position(self, user_id, position_id, sharechain_id):
        """刷新候选人链路信息，调用基础服务"""

        ret = yield self.thrift_candidate_ds.send_candidate_view_position(user_id, position_id, sharechain_id)
        self.logger.debug("send_candidate_view_position: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def send_candidate_interested(self, user_id, position_id, is_interested):
        """刷新候选人感兴趣，调用基础服务"""

        ret = yield self.thrift_candidate_ds.send_candidate_interested(user_id, position_id, is_interested)
        self.logger.debug("send_candidate_interested: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def get_candidate_list(self, post_user_id, click_time, is_recom, company_id):
        """获取候选人（要推荐的人）列表"""

        ret = yield self.thrift_candidate_ds.get_candidate_list(post_user_id, click_time, is_recom, company_id)

        self.logger.debug("get_candidate_list: %s" % ret)
        return ret

    @gen.coroutine
    def post_recommend(self, post_user_id, click_time, recom_record_id,
                       realname, company, position, mobile, recom_reason,
                       company_id):
        ret = yield self.thrift_candidate_ds.recommend(
            post_user_id, click_time, recom_record_id, realname, company,
            position, mobile, recom_reason, company_id)

        self.logger.debug("recommend_result: %s" % ret)
        return ret

    @gen.coroutine
    def post_ignore(self, recom_record_id, company_id, post_user_id,
                    click_time):
        ret = yield self.thrift_candidate_ds.ignore(
            recom_record_id, company_id, post_user_id,  click_time)

        self.logger.debug("recommend_result: %s" % ret)
        return ret

    @gen.coroutine
    def sorting(self, post_user_id, company_id):
        ret = yield self.thrift_candidate_ds.sort(
            post_user_id, company_id)

        self.logger.debug("sorting: %s" % ret)
        return ret

    @gen.coroutine
    def get_recommendations(self, company_id, list_of_recom_ids):
        ret = yield self.thrift_candidate_ds.get_recommendations(
            company_id, list_of_recom_ids)

        self.logger.debug("get_recommendations: %s" % ret)
        return ret

    @gen.coroutine
    def get_recommendation(self, recom_record_id, post_user_id):
        infra_ret = yield self.thrift_candidate_ds.get_recommendation(
            recom_record_id, post_user_id)
        self.logger.debug('infra_ret: %s' % infra_ret)

        ret = ObjectDict(
            position_name=infra_ret.title,
            recom=infra_ret.recom,
            click_time=infra_ret.clickTime,
            id=infra_ret.id,
            presentee_name=infra_ret.presenteeName,
            next=0 if infra_ret.nextOne else 1,
            # recom_total=infra_ret.recomTotal,
            # recom_index=infra_ret.recomIndex,
            # recom_ignore=infra_ret.recomIgnore
        )

        self.logger.debug("get_recommendation: %s" % ret)
        return ret
