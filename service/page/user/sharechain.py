# coding=utf-8

import tornado.gen as gen

import conf.common as const
from service.page.base import PageService
from util.tool.date_tool import curr_now
from util.common.decorator import log_coro
from util.common import ObjectDict
from util.tool.url_tool import make_static_url


class SharechainPageService(PageService):

    def __init__(self):
        super().__init__()

    @log_coro
    @gen.coroutine
    def refresh_share_chain(self, presentee_user_id=None, position_id=None,
                            share_chain_parent_id=None, forward_id=None):
        """
        对给定的 presentee_user_id 和 position_id 做链路原数据的入库操作
        :param presentee_user_id: 查看 JD 页的用户 wxsuer_id
        :param position_id: 被查看的职位 id
        :param share_chain_parent_id
        :param forward_id: 员工转发出去的职位链接上标识唯一性的参数
        :return: 如果创建链路愿数据成功,返回 True; 否则返回 False
        """

        assert presentee_user_id and position_id

        # 找到这个 user_id 最后访问该职位的点击记录
        last_share_record = yield self._get_latest_share_record(
            user_id=presentee_user_id, position_id=position_id)

        if not last_share_record:
            self.logger.debug("no need to refresh sharechain, skip...")
            return 0, 0

        # 找到 share_record 后创建 candiate_share_chain
        inserted_share_chain_id, depth = yield self._save_recom(
            last_share_record, share_chain_parent_id, forward_id)

        share_chain_rec = yield self._select_recom_record(
            position_id, presentee_user_id)

        if share_chain_rec:
            yield self._copy_to_candidate_recom_record(share_chain_rec)

        return inserted_share_chain_id, depth

    @log_coro
    @gen.coroutine
    def create_share_record(self, params):
        """创建分享链路"""

        record_id = yield self.candidate_position_share_record_ds.create_share_record({
            "wechat_id":         params.wechat_id,
            "recom_id":          params.recom_id,
            "position_id":       params.position_id,
            "presentee_id":      params.presentee_id,
            "presentee_user_id": params.presentee_user_id,
            "recom_user_id":     params.recom_user_id,
            "viewer_id":         params.viewer_id,
            "viewer_ip":         params.viewer_ip,
            "source":            params.source,
            "click_from":        params.click_from,
        })

        assert record_id
        raise gen.Return(record_id)

    @log_coro
    @gen.coroutine
    def _select_recom_record(self, position_id, user_id):
        # 现在无论是否开启挖掘被动求职者，都要放到链路表中
        record = yield self.candidate_share_chain_ds.get_share_chain(
            conds={
                "depth": [0, "!="],
                "presentee_user_id": user_id,
                "position_id": position_id
            },
            appends=['order by id desc']
        )
        raise gen.Return(record)

    @log_coro
    @gen.coroutine
    def _copy_to_candidate_recom_record(self, rec):
        yield self.candidate_recom_record_ds.insert_candidate_recom_record({
            "position_id":       rec.position_id,
            "presentee_user_id": rec.presentee_user_id,
            "click_time":        rec.click_time,
            "depth":             rec.depth,
            "repost_user_id":    rec.root2_recom_user_id,
            "post_user_id":      rec.root_recom_user_id
        })

    @log_coro
    @gen.coroutine
    def _get_latest_share_record(self, user_id, position_id):
        """获得最新的转发触发数据"""

        ret = yield self.candidate_position_share_record_ds.get_share_record(
            conds={
                "presentee_user_id": user_id,
                "position_id": position_id,
            },
            fields=[
                'id',
                'create_time',
                'wechat_id',
                'recom_user_id',
                'position_id',
                'presentee_user_id',
                'click_from',
            ],
            appends=[
                'AND `recom_user_id` != `presentee_user_id`',
                'ORDER BY create_time DESC'
            ]
        )
        raise gen.Return(ret)

    @log_coro
    @gen.coroutine
    def _is_valid_employee(self, position_id, user_id):
        """返回 user 是否是 position 所在企业的员工"""

        position = yield self.job_position_ds.get_position({
            "id": position_id
        })
        company_id = position.company_id

        is_valid_employee = yield self.infra_user_ds.is_valid_employee(user_id, company_id)
        return is_valid_employee

    @log_coro
    @gen.coroutine
    def _existed_record(self, share_record, share_chain_parent_id, forward_id):
        """检查原始链路数据中是否有该数据"""

        record = yield self.candidate_share_chain_ds.get_share_chain({
            "position_id":       share_record.position_id,
            "presentee_user_id": share_record.presentee_user_id,
            "recom_user_id": share_record.recom_user_id,
            "parent_id": share_chain_parent_id,
            "forward_id": forward_id
        })
        raise gen.Return(record)

    @log_coro
    @gen.coroutine
    def _existed_record_ignore_parent(self, share_record):
        """检查原始链路数据中是否有该数据, 忽略parent_id， 为10分钟消息推送卡片去重"""

        record = yield self.candidate_share_chain_ds.get_share_chain(
            {
                "position_id": share_record.position_id,
                "presentee_user_id": share_record.presentee_user_id,
                "recom_user_id": share_record.recom_user_id,
            },
            appends=["ORDER BY click_time desc", "LIMIT 1"]
        )
        raise gen.Return(record)

    @log_coro
    @gen.coroutine
    def _hr_remark_ignored_record(self, share_record):
        """检查这个候选人是否曾今被 hr 设置为 ignore"""

        # TODO (yiliang) 要改成不用 join 的 方式
        # 逻辑 SQL
        # SQL_CHECK_HR_CANDIDATE_REMARK = """
        # SELECT r.hraccount_id
        # FROM candidate_remark r
        # WHERE r.status = 2
        #   AND r.hraccount_id IN ( SELECT e.id FROM user_employee e
        #     JOIN job_position p ON p.company_id = e.company_id
        #     WHERE p.id = %s )
        #   AND r.user_id = %s
        # """

        ret = yield self.candidate_remark_ds.get_candidate_remark(
            conds={
                "status": 2,
                "user_id": share_record.presentee_user_id
            },

            fields=['hraccount_id'],

            appends=["""
            AND hraccount_id IN (
                SELECT e.id FROM user_employee e
                JOIN job_position p ON p.company_id = e.company_id
                WHERE p.id = %s
            )
            """ % share_record.position_id]
        )

        raise gen.Return(ret)

    @log_coro
    @gen.coroutine
    def _save_recom(self, last_share_record, share_chain_parent_id, forward_id):
        """ 入库链路数据 candidate_share_chain

        将浏览者置为关系最近的员工的初被动求职者
        如果链路中不存在员工，则将浏览者置为第一个转发人的被动求职者

        如果存在 share_chain_parent_id，基于上一条记录插入新记录
        如果不存在 share_chain_parent_id，
        说明这是一条首次转发带来的推荐记录，也就是说转发人并没有点击其他人的转发，而是自主打开 JD 页
        """

        ret = 0
        depth = 0

        # 如果是重复数据，更新click_time, click_from
        existed_record = yield self._existed_record(last_share_record, share_chain_parent_id, forward_id)
        if existed_record:
            yield self.candidate_share_chain_ds.update_share_chain(
                conds={
                    "position_id": last_share_record.position_id,
                    "parent_id": share_chain_parent_id,
                    "recom_user_id": last_share_record.recom_user_id,
                    "presentee_user_id": last_share_record.presentee_user_id,
                    "forward_id": forward_id
                },
                fields={
                    "click_time": last_share_record.create_time,
                    "click_from": last_share_record.click_from
                }
            )
            return existed_record.id, depth

        self.logger.debug("[SC]last_share_record: %s" % last_share_record)

        position_id = last_share_record.position_id

        presentee_user_is_valid_employee = yield self._is_valid_employee(
            position_id, last_share_record.presentee_user_id)

        record_ignore_parent = yield self._existed_record_ignore_parent(last_share_record)
        if record_ignore_parent:
            type_ = record_ignore_parent.type
        else:
            type_ = 0

        if presentee_user_is_valid_employee:

            ret = yield self.candidate_share_chain_ds.insert_share_chain({
                "position_id":         position_id,
                "presentee_user_id":   last_share_record.presentee_user_id,
                "recom_user_id":       last_share_record.presentee_user_id,
                "root_recom_user_id":  last_share_record.presentee_user_id,
                "root2_recom_user_id": 0,
                "click_time":          last_share_record.create_time,
                "depth":               0,
                "parent_id":           share_chain_parent_id if share_chain_parent_id else 0,
                "type":                type_,
                "forward_id":          forward_id,
                "click_from":          last_share_record.click_from
            })

        # 如果看的人不是员工，
        else:
            # 如果存在上游数据（last_node）， 转发链长度 + 1
            if share_chain_parent_id:

                parent_share_chain_record = yield self.candidate_share_chain_ds.get_share_chain({
                    "id": share_chain_parent_id
                })

                if parent_share_chain_record.depth == 1:
                    root2_to_insert = last_share_record.recom_user_id
                else:
                    root2_to_insert = parent_share_chain_record.root2_recom_user_id
                depth = parent_share_chain_record.depth + 1
                ret = yield self.candidate_share_chain_ds.insert_share_chain({
                    "position_id":         position_id,
                    "presentee_user_id":   last_share_record.presentee_user_id,
                    "recom_user_id":       last_share_record.recom_user_id,
                    "root_recom_user_id":  parent_share_chain_record.root_recom_user_id,
                    "root2_recom_user_id": root2_to_insert,
                    "click_time":          last_share_record.create_time,
                    "depth":               parent_share_chain_record.depth + 1,
                    "parent_id":           share_chain_parent_id,
                    "type":                type_,
                    "forward_id":          forward_id,
                    "click_from":          last_share_record.click_from
                })

            # 如果不存在上游数据，记录为 depth 1
            else:
                depth = 1
                ret = yield self.candidate_share_chain_ds.insert_share_chain({
                    "position_id":         position_id,
                    "presentee_user_id":   last_share_record.presentee_user_id,
                    "recom_user_id":       last_share_record.recom_user_id,
                    "root_recom_user_id":  last_share_record.recom_user_id,
                    "root2_recom_user_id": 0,
                    "click_time":          last_share_record.create_time,
                    "depth":               1,
                    "parent_id":           0,
                    "type":                type_,
                    "forward_id":          forward_id,
                    "click_from":          last_share_record.click_from
                    })

            # 查询 hr_candidate_remark, 如果对应数据被忽略，则设为新数据
            remark_record = yield self._hr_remark_ignored_record(last_share_record)
            if remark_record:
                self.logger.debug(
                    "[SC]renew candidate_remark: %s" % remark_record)

                yield self.candidate_remark_ds.update_candidate_remark(
                    conds={
                        "hraccount_id": remark_record.hraccount_id,
                        "user_id": last_share_record.presentee_user_id
                    },
                    fields={
                        "status": 0
                    }
                )

        return ret, depth

    @log_coro
    @gen.coroutine
    def _get_latest_recom_record(self, position_id, user_id, fixed_now):
        """
        SELECT *
        FROM candidate_share_chain
        WHERE position_id = %s AND
              presentee_user_id = %s AND
              click_time <= %s
        ORDER BY click_time DESC
        LIMIT 1
        """
        record = yield self.candidate_share_chain_ds.get_share_chain({
                "position_id": position_id,
                "presentee_user_id": user_id,
                "click_time": [fixed_now, "<="]
            },
            appends=['ORDER BY click_time DESC',
                     'LIMIT 1']
        )
        raise gen.Return(record)

    @log_coro
    @gen.coroutine
    def get_referral_employee_user_id(self, user_id=None, position_id=None):
        """返回 user_id 申请职位时,是否经过了员工内推
        如果经过了员工内推,返回内推员工 user_wx_user id

        :param user_id: 申请人 user_user id
        :param position_id: 被申请职位 id
        :return: 如果有内推员工,返回内推员工 user_user id;如果没有内推员工或参数不全
        ,返回 0.

        返回的内推员工 user_id 以这次申请点击时候的链路为准.
        如果这个用户看了其他包含员工转发的链路, 但是没有从这条链路申请职位,
            是不能正常获取到员工 wxuser id 的.
        """

        if user_id is None or position_id is None:
            return 0, 0

        is_employee = yield self._is_valid_employee(position_id, user_id)

        if is_employee:
            self.logger.debug("[SC]employee application, referral_employee_user_id = 0")
            return 0, 0

        fixed_now = curr_now()

        # 获取这条申请的 recom_record 条目
        share_chain_record = yield self._get_latest_recom_record(
            position_id, user_id, fixed_now)

        # 如果是直接点入申请职位的, 或者员工申请，不存在内推员工
        if not share_chain_record or share_chain_record.depth == 0:
            return 0, 0

        # 如果 depth = 1， 只需要查看该条记录的 recom_user_id 是否是员工即可
        elif share_chain_record.depth == 1:
            is_employee = yield self._is_valid_employee(
                position_id, share_chain_record.recom_user_id)
            if is_employee:
                return share_chain_record.recom_user_id, share_chain_record.depth
        else:
            # 多重转发
            # share_chain_record.depth > 1

            # 获取 share_chain_record 中的 root_recom_user_id
            root_recom_user_id = share_chain_record.root_recom_user_id
            click_time = share_chain_record.click_time

            # 查找 “最初推荐人” 的 recom_record 的记录，
            # 如果这条记录的 depth 是 0，那么这条记录就是内推
            share_chain_of_root = yield self._get_latest_recom_record(
                    position_id, root_recom_user_id, click_time)

            if share_chain_of_root and share_chain_of_root.depth == 0:
                return share_chain_of_root.recom_user_id, share_chain_of_root.depth

            # 如果查不到最初联系人, 说明这条链路没有被员工截断过
            # 并且 recom_id 这个人是自己点 JD 页访问的
            else:
                root_recom_user_is_employee = yield self._is_valid_employee(
                    position_id, root_recom_user_id)
                if root_recom_user_is_employee:
                    return root_recom_user_id, share_chain_record.depth

        return 0, 0

    @log_coro
    @gen.coroutine
    def is_employee_presentee(self, share_chain_id):
        """返回 share_chain_id 所指向的 share chain record 是不是员工一度点击

        先查询 share_chain_id 指向的记录是否有 parent
        如果有 parent 且 parent share chain record 是员工所转发出的点击，返回 True
        否则返回 False
        仅限于红包调用
        :param share_chain_id:
        :return: bool
        """

        if not share_chain_id:
            raise gen.Return(False)

        share_chain = yield self.candidate_share_chain_ds.get_share_chain({
            "id": share_chain_id
        })

        if not share_chain:
            return False

        if share_chain.parent_id:
            parent_share_chain = yield self.candidate_share_chain_ds.get_share_chain({
                "id": share_chain.parent_id
            })

            valid_employee = yield self._is_valid_employee(
                parent_share_chain.position_id,
                parent_share_chain.recom_user_id)

            raise gen.Return(
                parent_share_chain and
                (
                    parent_share_chain.depth == 0 or
                    parent_share_chain.depth == 1 and
                    valid_employee and
                    parent_share_chain.parent_id == 0
                )
            )
        else:
            valid_employee = yield self._is_valid_employee(
                share_chain.position_id,
                share_chain.recom_user_id)
            return valid_employee

    @log_coro
    @gen.coroutine
    def find_last_psc(self, position_id, presentee_user_id):
        """根据职位和查看者寻找最近的链路记录"""
        parent_share_chain = yield self.candidate_share_chain_ds.get_share_chain(
            conds={
                "position_id": position_id,
                "presentee_user_id": presentee_user_id
            },
            appends=['ORDER BY click_time DESC',
                     'LIMIT 1'])
        if parent_share_chain:
            raise gen.Return(parent_share_chain.id)
        else:
            raise gen.Return(0)

    @gen.coroutine
    def find_candidate_by_position(self, position, num=25):
        """根据职位id获取浏览该职位的候选人"""
        users = []
        records = yield self.candidate_position_share_record_ds.get_share_record_list(
            conds={
                "position_id": position.id
            },
            appends=["group by presentee_user_id", "order by create_time desc", "LIMIT {}".format(num)]
        )
        for r in records:
            user = ObjectDict()
            user_id = r.presentee_user_id
            user_info = yield self.infra_user_ds.infra_get_user(conds={"id": user_id})
            user['name'] = user_info.name or user_info.nickname
            user['headimg'] = make_static_url(user_info.headimg or const.SYSUSER_HEADIMG)
            user['is_hack'] = False
            candidate_position = yield self.candidate_position_ds.get_candidate_position(conds={
                "position_id": position.id,
                "user_id": user_id
            })
            user['viewnum'] = candidate_position.view_number or 1
            user['click_from'] = r.click_from or 2
            user['click_time'] = r.create_time
            user['position_title'] = position.title
            user['id'] = user_id
            users.append(user)
        return users

    @gen.coroutine
    def get_share_chain_by_id(self, share_chain_id):
        """根据share_chain_id获取share_chain"""
        ret = yield self.candidate_share_chain_ds.get_share_chain(conds={"id": share_chain_id})
        raise gen.Return(ret)
