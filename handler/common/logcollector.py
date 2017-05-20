# coding=utf-8

from functools import partialmethod
import time

from handler.base import BaseHandler


class LogCollectorHandler(BaseHandler):
    # 专接前端log

    def post(self):
        log_it = self.dispatch()
        log_it()

    def dispatch(self):
        self.guarantee("action", "target")
        action = self.params.action
        target = self.params.target
        try:
            method = getattr(self, "_".join([action, target]))
        except AttributeError:
            method = self.method_missing
        return method

    def log_it(self, *fields):
        log = self.gen_log(*fields)
        self.logger.stats(log)

    def gen_log(self, *fields):
        self.guarantee(*fields)
        log = self._gen_basic_log()
        for p in fields:
            log.update({
                p: self.params[p]
            })
        return log

    def _gen_basic_log(self):
        return {
            "for": "persona",
            "action": self.params.action,
            "target": self.params.target,
            "time_stamp": time.time(),
            "user": {
                'id': self.current_user.sysuser.id
            }
        }

    def method_missing(self):
        self.logger.error(
            "class: {}, log method missing error, json_args: {}".format(self.__class__.__name__, self.params))

    # 可以通过单独定义方法处理复杂log
    # 公司相关
    visit_company = \
        share_timeline_company = \
        share_friends_company = partialmethod(log_it, "company_id")

    # 职位相关
    visit_position_index = \
        visit_position_detail = \
        share_timeline_position_index = \
        share_timeline_position_detail = \
        share_friends_position_index = \
        share_friends_position_detail = partialmethod(log_it, "company_id", "position_id")

    # 团队相关
    visit_team_detail = \
        share_timeline_team = \
        share_friends_team = partialmethod(log_it, "company_id", "team_id")

    # 职位列表相关
    visit_position_list = \
        share_timeline_position_list = \
        share_friends_position_list = search_position_list = partialmethod(log_it, "search_conditions")

    # 访问profile
    visit_profile = partialmethod(log_it)
