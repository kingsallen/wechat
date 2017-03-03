# coding=utf-8

from tornado import gen
import conf.path as path
from service.page.base import PageService
from util.common import ObjectDict
from util.tool.url_tool import make_url

class CustomPageService(PageService):

    """企业定制化相关内容"""

    # 诺华集团招聘
    _SUPPRESS_APPLY_CIDS = [61153]

    # 开启代理投递
    # e袋洗
    _AGENT_APPLY_CIDS = [926]

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
        is_suppress_apply, suppress_apply_data=self._is_suppress_apply(position_info)
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
            'is_delegate_drop':  self._is_edx_wechat(current_wechat, current_employee),
            'delegate_drop_url': make_url(path.CUSTOMIZE_EDX, params, recom_friend=1)
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

