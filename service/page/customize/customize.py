# coding=utf-8

from tornado import gen
import conf.path as path
from service.page.base import PageService
from util.common import ObjectDict
from util.tool.url_tool import make_url


class CustomizePageService(PageService):
    """企业定制化相关内容"""

    # 诺华集团招聘
    _SUPPRESS_APPLY_CIDS = [61153]

    # 开启代理投递
    # e袋洗
    _AGENT_APPLY_CIDS = [926]

    # 雅诗兰黛直接投递
    _DIRECT_APPLY = [82]

    # 宝洁投递成功提示页面
    _APPLY_SUCCESS = [1753]

    # 蓝色光标定制：
    # 在团队列表页面, 显示团队简介, 而不是团队详情
    _BLUE_FOCUS_COMPANY_ID = 52813

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def _is_suppress_apply(self, position_info):
        if position_info.company_id not in self._SUPPRESS_APPLY_CIDS:
            return False, None
        else:
            return (True, {"custom_field": position_info.job_custom or "",
                           "job_number": position_info.jobnumber or ""})

    @gen.coroutine
    def get_suppress_apply(self, position_info):
        """
        诺华集团定制。
        目的：禁止在仟寻平台投递，点击我要投递，弹出下一步操作步骤
        :param position_info:
        :return:
        """
        is_suppress_apply, suppress_apply_data = yield self._is_suppress_apply(position_info)
        return ObjectDict({
            "is_suppress_apply": is_suppress_apply,
            "suppress_apply_data": suppress_apply_data
        })

    def _is_edx_wechat(self, current_wechat, current_employee):
        """
        判断是否为代理投递目标用户
        :param current_wechat:
        :param current_employee:
        :return:
        """
        if (current_wechat.company_id in self._AGENT_APPLY_CIDS and current_employee.id):
            return True
        return False

    @gen.coroutine
    def get_delegate_drop(self, current_wechat, current_employee, params):
        return ObjectDict({
            'is_delegate_drop': self._is_edx_wechat(current_wechat, current_employee),
            'delegate_drop_url': make_url(path.CUSTOMIZE_EDX, params, self.settings.platform_host, recom_friend=1)
        })

    @gen.coroutine
    def create_campaign_email_agentdelivery(self, params):
        """
        创建 Email 代理投递记录
        :param params:
        {
            "company_id": "",
            "position_id": "",
            "employee_id": "",
            "friendname": "",
            "email": "",
            "code": "",
        }
        :return:
        """

        res = yield self.create_campaign_email_agentdelivery(params)
        raise gen.Return(res)

    @gen.coroutine
    def create_esteelauder_apply(self, company_id, app_cv_config_id):
        """
        雅诗兰黛直接投递
        :param company_id:
        :param app_cv_config_id:
        :return:
        """

        is_esteelauder = False
        if (company_id in self._DIRECT_APPLY and
                app_cv_config_id):
            self.logger.debug("雅诗兰黛特殊处理: 直接投递")
            is_esteelauder = True

        return is_esteelauder

    @gen.coroutine
    def get_pgcareers_msg(self, company_id):
        """
        申请成功后，跳转到宝洁宝洁页面
        :param company_id:
        :return:
        """
        message = ""
        if company_id in self._APPLY_SUCCESS:
            message = '<p>恭喜申请成功!</p><p>请务必在网申截至时间前到宝洁官网</p>' + \
                      '<p><a href="http://china.pgcareers.com/">http://china.pgcareers.com/</a></p>' + \
                      '<p>完成网申, 网申前请仔细阅读网申指南呦!</p>'

        raise gen.Return(message)

    def blue_focus_team_index_show_summary_not_description(self, company, teams):
        """
        蓝色光标的定制, 在团队列表页面, 显示团队简介, 而不是团队详情
        :param company:
        :param teams:
        :return:
        """
        if company.id == self._BLUE_FOCUS_COMPANY_ID:
            for team in teams:
                team.description = team.summary
        else:
            pass
