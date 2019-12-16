# coding=utf-8

from tornado import gen

import conf.common as const
from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated
from util.common.exception import InfraOperationError
from util.common import ObjectDict


class PrivacyHandler(BaseHandler):
    """
    隐私协议
    """

    @handle_response
    @gen.coroutine
    def post(self):
        """
        是否同意弹出的"隐私协议": 用户如果点击同意，删除user_privacy_record表相关记录，如果拒绝，不删除
        -path: /api/privacy/agree
        -params:
        {
            "agree": 1, // 1: 同意， 0: 不同意
        }
        :return: {
            "status": 0,
            "message": "success"
        }

        """
        user_id = self.current_user.sysuser.id
        status = self.json_args.get('qx_agree')
        custom_agree = self.json_args.get('custom_agree')

        # 同意"仟寻隐私协议"
        if status is None:
            result = ObjectDict(status=0)
        else:
            result = yield self.privacy_ps.if_agree_privacy(user_id, status)
        # 用户同意"客户自定义隐私协议"，插入记录
        if custom_agree:
            custom_privacy = yield self.privacy_ps.if_agree_custom_privacy(user_id, self.current_user.company.id)
        else:  # custom_agree为None[同意"仟寻隐私协议"]或者为0【不同意，不需要插入数据】
            custom_privacy = ObjectDict(code='0')

        if result.status == const.API_SUCCESS and custom_privacy.code == const.NEWINFRA_API_SUCCESS:
            self.send_json_success()
        else:
            self.send_json_error(message=result.message or custom_privacy.message)


class IsAgreePrivacyHandler(BaseHandler):
    """
    用户是否同意过隐私协议 [用于决定是否需要弹出隐私协议]
    """

    @handle_response
    @gen.coroutine
    def get(self):
        """
        用户是否同意过隐私协议：【以前：data=0表示同意过，1表示没同意过。user_privacy_record有记录表示拒绝，没有记录表示同意过】
                            【现在：0 同意了最新的版本的隐私协议  1 未同意过任何版本的隐私协议  2 同意了老版本的隐私协议】
        -path: /api/privacy/is_agree/
        :return: {
            "status": 0,
            "message": "success",
            "data": 1
        }

        新用户：只有特定页面打开新协议
        老用户已经同意老协议：打开任何网页都弹出新协议，如果拒绝，特殊页面需要弹层同意才能访问，其它页面可以继续访问，24小时之后进任意界面还需要弹层
        老用户拒绝老协议：跟新用户一致【只有同意过新协议的用户返回true】
        注意：第一、三种用户跟以前一致，只有第二种情况需要再分情况：user_privacy_record没有记录【已经同意老协议】，如果已经同意新协议无需再弹层，如果拒绝新协议，不同页面需要做不同处理
        """
        user_id = self.current_user.sysuser.id
        # 获取仟寻隐私协议状态
        result, show_privacy_agreement = yield self.privacy_ps.if_privacy_agreement_window(user_id)

        # 获取客户自定义隐私协议开关
        custom_privacy_oms = yield self.company_ps.check_oms_switch_status(
            self.current_user.company.id,
            "客户自定义隐私协议"
        )
        if custom_privacy_oms.status != const.API_SUCCESS:
            raise InfraOperationError(custom_privacy_oms.message)

        if result:
            if custom_privacy_oms.data.get('valid'): # oms开关打开
                # 获取用户客户自定义隐私协议状态
                custom_privacy_status = yield self.privacy_ps.if_custom_privacy_window(user_id, self.current_user.company.id)
                if custom_privacy_status.data:  # 同意过
                    data = ObjectDict(qx_privacy=show_privacy_agreement,
                                      custom_privacy={"agree": custom_privacy_status.data}
                                      )
                else:   # 没同意过
                    custom_privacy_info = yield self.privacy_ps.get_custom_privacy_info(self.current_user.company.id)  # 获取客户自定义隐私协议信息
                    if custom_privacy_info.data:
                        if not custom_privacy_info.data.title and not custom_privacy_info.data.title.strip() and not custom_privacy_info.data.content and not custom_privacy_info.data.content.strip():
                            custom_privacy_info.data.title = custom_privacy_info.data.etitle
                            custom_privacy_info.data.content = custom_privacy_info.data.econtent
                        elif not custom_privacy_info.data.etitle and not custom_privacy_info.data.etitle.strip() and not custom_privacy_info.data.econtent and not custom_privacy_info.data.econtent.strip():
                            custom_privacy_info.data.etitle = custom_privacy_info.data.title
                            custom_privacy_info.data.econtent = custom_privacy_info.data.content
                        custom_privacy_info.data.update({"agree": custom_privacy_status.data})
                        data = ObjectDict(qx_privacy=show_privacy_agreement,
                                          custom_privacy=custom_privacy_info.data)
                    else: # 客户自定义隐私协议为空则不弹
                        data = ObjectDict(qx_privacy=show_privacy_agreement,
                                          custom_privacy=None
                                          )
            else: # oms开关关闭
                data = ObjectDict(qx_privacy=show_privacy_agreement,
                                  custom_privacy=None)
            self.send_json_success(data=data)
        else:
            self.send_json_error(message=show_privacy_agreement.message)
