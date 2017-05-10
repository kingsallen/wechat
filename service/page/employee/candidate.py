# coding=utf-8

from tornado import gen
from service.page.base import PageService
from util.common import ObjectDict


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

        self.logger.debug("ignore_result: %s" % ret)
        return ret

    @gen.coroutine
    def sorting(self, post_user_id, company_id):
        infra_ret = yield self.thrift_candidate_ds.sort(
            post_user_id, company_id)

        ret = ObjectDict({
            'recom_count': infra_ret.count,
            'rank': infra_ret.rank,
            'hongbao': infra_ret.hongbao
        })

        self.logger.debug("sorting: %s" % ret)
        return ret

    @gen.coroutine
    def get_recommendations(self, company_id, list_of_recom_ids):
        thrift_res = yield self.thrift_candidate_ds.get_recommendations(
            company_id, list_of_recom_ids)

        # 转换一下属性的命名
        ret = ObjectDict()
        ret.presentee_name = thrift_res.presenteeName
        ret.recom_total = thrift_res.recomTotal
        ret.id = thrift_res.id
        ret.recom_index = thrift_res.recomIndex
        ret.next_one = thrift_res.nextOne
        ret.position_name = thrift_res.positionName
        ret.recom_ignore = thrift_res.recomIgnore
        ret.click_time = thrift_res.clickTime

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
            presentee_name=infra_ret.presenteeName
        )

        self.logger.debug("get_recommendation: %s" % ret)
        return ret
