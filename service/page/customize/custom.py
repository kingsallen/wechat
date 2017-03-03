# coding=utf-8

from tornado import gen
from service.page.base import PageService
from util.common import ObjectDict

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

    @gen.coroutine
    def get_delegate_drop(self, handler):
        return {
            'is_delegate_drop':  self.is_edx_wechat(handler),
            'delegate_drop_url':  make_url("/mobile/custom/edx", handler.params, m='recom_friend')
        }
