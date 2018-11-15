# coding=utf-8

from tornado import gen
from service.page.base import PageService
from util.common import ObjectDict
import conf.common as const


class CandidatePageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def send_candidate_view_position(self, user_id, position_id, sharechain_id):
        """刷新候选人链路信息，调用基础服务"""

        ret = yield self.thrift_candidate_ds.send_candidate_view_position(user_id, position_id, sharechain_id)
        raise gen.Return(ret)

    @gen.coroutine
    def send_candidate_interested(self, user_id, position_id, is_interested):
        """刷新候选人感兴趣，调用基础服务"""

        ret = yield self.thrift_candidate_ds.send_candidate_interested(user_id, position_id, is_interested)
        raise gen.Return(ret)

    @gen.coroutine
    def get_candidate_list(self, post_user_id, click_time, is_recom, company_id):
        """获取候选人（要推荐的人）列表"""

        ret = yield self.thrift_candidate_ds.get_candidate_list(post_user_id, click_time, is_recom, company_id)
        return ret

    @gen.coroutine
    def add_candidate_company(self, user_id, mobile, company_id, name, nickname, email, recom_id):
        """增加候选人记录"""
        candidate = self.candidate_company_ds.get_candidate_company({
            "sys_user_id": user_id,
            "company_id": company_id,
            "status": const.YES
        })
        if candidate:
            yield self.candidate_company_ds.update_candidate_company(
                conds={
                    "sys_user_id": user_id,
                    "company_id": company_id,
                    "status": const.YES
                },
                fields={
                    "mobile": mobile,
                    "name": name,
                    "nickname": nickname,
                    "email": email}
            )
        else:
            yield self.candidate_company_ds.insert_candidate_company(
                fields=ObjectDict({
                    "sys_user_id": user_id,
                    "company_id": company_id,
                    "mobile": mobile,
                    "name": name,
                    "nickname": nickname,
                    "email": email,
                    "status": const.YES,
                    "is_recommend": const.YES if recom_id else const.NO,
                })
            )
        return

    @gen.coroutine
    def add_candidate_remard(self, user_id, company, position, name, hr_id):
        """增加候选人备注信息"""
        remark = yield self.candidate_remark_ds.get_candidate_remark({
            "user_id": user_id
        })
        if remark:
            yield self.candidate_remark_ds.update_candidate_remark(
                conds={
                    "user_id": user_id
                },
                fields={
                    "current_company": company,
                    "current_position": position,
                    "name": name,
                    "hraccount_id": hr_id
                }
            )
        else:
            yield self.candidate_remark_ds.insert_candidate_remark(
                fields=ObjectDict({
                    "user_id": user_id,
                    "current_company": company,
                    "current_position": position,
                    "name": name,
                    "hraccount_id": hr_id
                })
            )
        return

    @gen.coroutine
    def post_recommend(self, post_user_id, click_time, recom_record_id,
                       realname, company, position, mobile, recom_reason,
                       company_id, gender, email):
        infra_ret = yield self.thrift_candidate_ds.recommend(
            post_user_id, click_time, recom_record_id, realname, company,
            position, mobile, recom_reason, company_id, gender, email)

        ret = ObjectDict(
            next_one=infra_ret.nextOne,
            position_name=infra_ret.positionName,
            recom_index=infra_ret.recomIndex,
            id=infra_ret.id,
            click_time=infra_ret.clickTime,
            recom_ignore=infra_ret.recomIgnore,
            recom_total=infra_ret.recomTotal,
            presentee_name=infra_ret.presenteeName
        )

        return ret

    @gen.coroutine
    def post_ignore(self, recom_record_id, company_id, post_user_id,
                    click_time):
        infra_ret = yield self.thrift_candidate_ds.ignore(
            recom_record_id, company_id, post_user_id, click_time)

        ret = ObjectDict(
            next_one=infra_ret.nextOne,
            position_name=infra_ret.positionName,
            recom_index=infra_ret.recomIndex,
            id=infra_ret.id,
            click_time=infra_ret.clickTime,
            recom_ignore=infra_ret.recomIgnore,
            recom_total=infra_ret.recomTotal,
            presentee_name=infra_ret.presenteeName
        )

        return ret

    @gen.coroutine
    def sorting(self, post_user_id, company_id):
        infra_ret = yield self.thrift_candidate_ds.sort(
            post_user_id, company_id)

        if infra_ret:
            ret = ObjectDict({
                'recom_count': infra_ret.count,
                'rank': infra_ret.rank,
                'hongbao': infra_ret.hongbao
            })

            return ret

    @gen.coroutine
    def get_recommendations(self, company_id, list_of_recom_ids):
        thrift_res = yield self.thrift_candidate_ds.get_recommendations(
            company_id, list_of_recom_ids)
        if thrift_res:
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
            return ret
        else:
            return None

    @gen.coroutine
    def get_recommendation(self, recom_record_id, post_user_id):
        infra_ret = yield self.thrift_candidate_ds.get_recommendation(
            recom_record_id, post_user_id)
        ret = ObjectDict(
            position_name=infra_ret.title,
            recom=infra_ret.recom,
            click_time=infra_ret.clickTime,
            id=infra_ret.id,
            presentee_name=infra_ret.presenteeName
        )
        return ret
