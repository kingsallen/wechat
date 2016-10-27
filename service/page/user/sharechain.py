# coding=utf-8

import tornado.gen as gen
import conf.common as const
from util.tool.http_tool import http_post

from util.common import ObjectDict
from service.page.base import PageService
from util.tool.date_tool import curr_now
from setting import settings


class SharechainPageService(PageService):

    def __init__(self, logger):
        super().__init__(logger)

    @gen.coroutine
    def refresh_share_chain(self, wxuser_id=None, position_id=None):
        """
        对给定的 wxuser_id 和 position_id 做链路原数据的入库操作
        :param wxuser_id: 查看 JD 页的用户 wxsuer_id
        :param position_id: 被查看的职位 id
        :return: 如果创建链路愿数据成功,返回 True; 否则返回 False
        """

        assert wxuser_id and position_id

        # 找到这个 wxuser_id 最后访问该职位的点击记录
        share_record = yield self._get_latest_share_record(
            wxuser_id, position_id)

        if share_record:
            # 找到 share_record 后创建 stats.recom_record
            yield self._save_recom(share_record)

            rec = yield self._select_recom_record_real_time(position_id, wxuser_id)
            if rec:
                yield self._copy_to_candidate_recom_record(rec)

            raise gen.Return(True)
        else:
            raise gen.Return(False)

    @gen.coroutine
    def _select_recom_record_real_time(self, position_id, wxuser_id):
        # 现在无论是否开启挖掘被动求职者，都要放到链路表中
        record = self.stats_recom_record_ds.get_stats_recom_record(
            conds={
                "depth": [0, "!="],
                "presentee_id": wxuser_id,
                "position_id": position_id
            },
            fields=['position_id', 'presentee_id', 'click_time', 'depth', 'recom_id_2', 'recom_id'],
            appends=['order by id desc']
        )
        raise gen.Return(record)

    @gen.coroutine
    def _copy_to_candidate_recom_record(self, rec):
        yield self.candidate_recom_record_ds.insert_candidate_recom_record({
            "position_id":  rec.position_id,
            "presentee_id": rec.presentee_id,
            "depth":        rec.depth,
            "recom_id":     rec.recom_id,
            "recom_id_2":   rec.recom_id_2,
            "click_time":   rec.click_time
        })

    @gen.coroutine
    def _get_latest_share_record(self,wxuser_id, position_id):
        """获得最新的转发触发数据"""
        ret = yield self.candidate_recom_record_ds.get_share_record(
            conds={
                "presentee_id": wxuser_id,
                "position_id": position_id,
                "recom_id": ["presente_id", "!="],
            },
            fields=['create_time', 'wechat_id', 'recom_id', 'position_id', 'presentee_id'],
            appends=['ORDER BY create_time DESC']
        )
        raise gen.Return(ret)

    @gen.coroutine
    def _is_valid_employee(self, position_id, wxuser_id):
        """返回 wxuser 是否是 position 所在企业的员工
        """
        position = yield self.position_ds.get_position({
            "id": position_id
        })
        company_id = position.company_id

        employee = yield self.user_employee_ds.get_employee({
            "wxuser_id": wxuser_id,
            "company_id": company_id,
            "activation": const.OLD_YES,
            "disable": const.OLD_YES,
            "status": const.OLD_YES
        })
        raise gen.Return(bool(employee))

    @gen.coroutine
    def _no_existed_record(self, recom):
        """检查原始链路数据中是否有该数据"""
        record = yield self.stats_recom_record_dao.get_stats_recom_record(
            conds={
                "position_id": recom.position_id,
                "presentee_id": recom.presentee_id,
                "click_time": recom.create_time
            })
        raise gen.Return(bool(record))

    @gen.coroutine
    def _get_recom_history_record(self, position_id, recom_id, create_time):
        recom = yield self.stats_recom_record_ds.get_stats_recom_record(
            conds={
                "position_id": position_id,
                "presentee_id": recom_id,
                "click_time": [create_time, "<"]
            },
            appends=['order by id desc']
        )
        raise gen.Return(recom)

    @gen.coroutine
    def _hr_remark_ignored_record(self, recom):
        """检查这个候选人是否曾今被 hr 设置为 ignore
        """

        # TODO (yiliang) 要改成不用 join 的 方式
        # 逻辑 SQL
        # SQL_CHECK_HR_CANDIDATE_REMARK = """
        # SELECT r.hraccount_id
        # FROM candidate_remark r
        # WHERE r.status = 2
        #   AND r.hraccount_id IN ( SELECT e.id FROM user_employee e
        #     JOIN job_position p ON p.company_id = e.company_id
        #     WHERE p.id = %s )
        #   AND r.wxuser_id = %s
        # """

        record = self.candidate_remark_ds.get_candidate_remark(
            conds={"status": 2, "wxuser_id": recom.wxuser_id},
            fields=['hraccount_id'],
            appends=["""AND hraccount_id IN ( SELECT e.id FROM user_employee e
            JOIN job_position p ON p.company_id = e.company_id
            WHERE p.id = %s )""" % recom.position_id]
        )
        raise gen.Return(record)

    @gen.coroutine
    def _save_recom(self, recom):
        """ 处理转发轨迹
        将浏览者置为关系最近的员工的初被动求职者
        如果链路中不存在员工，则将浏览者置为第一个转发人的被动求职者

        Args:
            l: 转发记录
        """

        # 如果看的人是员工，记录为 level 0， recom_id 为自己，
        #   recom_id_2 为空， last_recom_id 为空
        is_employee = yield self._is_valid_employee(recom.position_id, recom.presentee_id)

        no_existed_record = yield self._no_existed_record(recom)

        if is_employee and no_existed_record:
            self.logger.debug(
                "position_id:%s,recom_id:%s,presentee_id:%s" %
                (recom.position_id, recom.presentee_id, recom.presentee_id))

            yield self.stats_recom_record_ds.insert_stats_recom_record({
                    "position_id": recom.position_id,
                    "presentee_id": recom.presentee_id,
                    "click_time": recom.create_time,
                    "depth": 0,
                    "recom_id_2": 0,
                    "recom_id": recom.presentee_id,
                    "last_recom_id": 0
                })
        # 如果看的人不是员工，
        else:
            # 如果数据已经记录，则不会重复记录
            if no_existed_record:
                last_node = yield self._get_recom_history_record(
                    recom.position_id, recom.recom_id, recom.create_time)

                # 如果存在上游数据（last_node）， 转发链长度 + 1
                if last_node:
                    print("position_id:%s,recom_id:%s,presentee_id:%s" %
                          (recom.position_id, last_node.recom_id,
                           recom.presentee_id))

                    yield self.stats_recom_record_ds.insert_stats_recom_record(
                        {
                            "position_id":   recom.position_id,
                            "presentee_id":  recom.presentee_id,
                            "click_time":    recom.create_time,
                            "depth":         last_node.depth + 1,
                            "recom_id_2":    recom.recom_id if last_node.depth == 1 else last_node.recom_id_2,
                            "recom_id":      recom.recom_id,
                            "last_recom_id": recom.recom_id
                        })

                # 如果不存在上游数据，记录为 level 1， recom_id_2 为空，
                #   last_recom_id 为 recom_id
                else:
                    print("position_id:%s,recom_id:%s,presentee_id:%s" %
                          (recom.position_id, recom.recom_id, recom.presentee_id))
                    yield self.stats_recom_record_ds.insert_stats_recom_record(
                        {
                            "position_id":   recom.position_id,
                            "presentee_id":  recom.presentee_id,
                            "click_time":    recom.create_time,
                            "depth":         1,
                            "recom_id_2":    0,
                            "recom_id":      recom.recom_id,
                            "last_recom_id": recom.recom_id
                        })

                # 查询 hr_candidate_remark, 如果对应数据被忽略，则设为新数据
                remark_record = yield self._hr_remark_ignored_record(recom)
                if remark_record:
                    self.logger.debug("renew candidate_remark: hraccount_id:%s,wxuser_id:%s" %
                        (remark_record['hraccount_id'], recom['presentee_id']))

                    yield self.candidate_remark_ds.update_candidate_remark(
                        conds={
                            "hraccount_id": remark_record.hraccount_id,
                            "wxuser_id": recom.presentee_id
                        },
                        fields={"status": 0}
                    )
