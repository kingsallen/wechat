# coding=utf-8

from tornado import gen

import conf.common as const
from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated


class ReleasedPositionHandler(BaseHandler):
    """已发布职位管理"""

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):

        # 选择正确的user用户
        hr_wx_user = yield self.position_ps.get_hr_wx_user(self.current_user.sysuser.unionid, self.current_user.wechat.id)

        if not self.current_user.wxuser.unionid:
            self.write_error(403)
            return

        # 招聘助手用户
        hr_info = yield self.position_ps.get_hr_info_by_wxuser_id(hr_wx_user.id)

        # 暂未注册雇主平台
        if not hr_info or hr_info.company_id == 0:
            self.render(template_name="refer/weixin/wx_published_position_list/wx_published_position_list.html", positions='')
            return

        pageSize = self.params.pageSize or 20
        pageNumber = self.params.pageNumber or 0

        conds = {
            "status": [1, "!="],
            "company_id": hr_info.company_id,
        }
        if hr_info.account_type == 1:
            # 子帐号，限定只展示子帐号发布的职位，否则暂时所有职位
            conds.update({
                "publisher": hr_info.id
            })

        positions_list = yield self.position_ps.get_positions_list(
            conds=conds,
            fields=None,
            appends=[
                "ORDER BY update_time DESC",
                "LIMIT {}, {}".format(pageNumber*pageSize, (pageNumber + 1)*pageSize)
            ]
        )

        for item in positions_list:
            count = yield self.application_ps.get_position_applied_cnt(conds={
                "position_id": item.id,
                "email_status": const.NO,
            }, fields=["id"])

            item['resume_num'] = count.get("count_id", 0)

        # ---8<---8<--- KA 用户跳转到企业号 start ---8<---8<---8<---8<---
        signature = None
        company_id = hr_info.company_id
        company_info = yield self.company_ps.get_company(
            conds={'id': company_id})
        company_type = company_info.type

        if company_type == 0:
            wechat_info = yield self.wechat_ps.get_wechat(
                conds={'company_id': company_id})
            if wechat_info:
                signature = wechat_info.signature
        # ---8<---8<--- KA 用户跳转到企业号 end ---8<---8<---8<---8<---

        self.render(template_name="refer/weixin/wx_published_position_list/wx_published_position_list.html",
                    positions = positions_list, signature=signature)
