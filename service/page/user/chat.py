# coding=utf-8
import json

import pypinyin
from pypinyin import lazy_pinyin
from tornado import gen

import conf.common as const
from service.page.base import PageService
from setting import settings
from util.common import ObjectDict
from util.common.decorator import log_time
from util.tool.date_tool import str_2_date
from util.tool.http_tool import http_post, http_get
from util.tool.str_tool import gen_salary
from util.tool.url_tool import make_static_url


class ChatPageService(PageService):
    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_chatrooms(self, user_id, page_no, page_size):
        """获得聊天室列表"""

        ret = yield self.thrift_chat_ds.get_chatrooms_list(user_id, page_no, page_size)
        obj_list = list()
        if ret.rooms:
            for e in ret.rooms:
                room = ObjectDict()
                room['id'] = e.id
                room['hr_id'] = e.hrId
                room['hr_name'] = e.name or "HR"
                room['hr_headimg'] = make_static_url(e.headImgUrl or e.companyLogo or const.HR_HEADIMG)
                room['company_name'] = e.companyName
                room['chat_time'] = str_2_date(e.createTime, self.constant.TIME_FORMAT_MINUTE)
                room['unread_num'] = e.unReadNum
                obj_list.append(room)

        raise gen.Return(obj_list)

    @gen.coroutine
    def get_chats(self, room_id, page_no, page_size):
        """获得聊天历史记录"""

        ret = yield self.thrift_chat_ds.get_chats(room_id, page_no, page_size)
        self.logger.debug(ret)
        obj_list = list()
        if ret.chatLogs:
            for e in ret.chatLogs:
                room = ObjectDict()
                room['id'] = e.id
                room['content'] = e.content or ''
                room['chatTime'] = str_2_date(e.createTime, const.TIME_FORMAT)
                room['speaker'] = e.speaker  # 0：求职者，1：HR
                room['msgType'] = e.msgType
                room['compoundContent'] = json.loads(e.compoundContent if e.compoundContent else '{}') or {}
                room['stats'] = json.loads(e.stats if e.stats else '{}') or {}
                self._compliant_chat_log(e, room)
                obj_list.append(room)

        raise gen.Return(obj_list)

    @staticmethod
    def _compliant_chat_log(message, room):
        """兼容老的聊天字段"""
        btn_content = json.loads(message.btnContent) if message.btnContent else message.btnContent
        if btn_content and type(btn_content) == str:
            btn_content = json.loads(btn_content)
        duration = message.duration
        server_id = message.serverId
        asset_url = message.assetUrl
        if type(room['compoundContent']) == dict:
            room['compoundContent'].update(duration=duration, server_id=server_id, asset_url=asset_url)
        if message.msgType == 'button':
            room['compoundContent'] = btn_content

    @gen.coroutine
    def get_chatroom(self, user_id, hr_id, company_id, position_id, room_id, qxuser, is_gamma, mobot_enable,
                     recom, is_employee):
        """进入聊天室"""
        hr_info = ObjectDict()
        mobot_info = ObjectDict(enable=mobot_enable, name='', headimg='')

        ret = yield self.thrift_chat_ds.enter_chatroom(user_id, hr_id, position_id, room_id, is_gamma)
        if ret.hr:
            hr_info = ObjectDict(
                hr_id=ret.hr.hrId,
                hr_name=ret.hr.hrName or "HR",
                hr_headimg=make_static_url(ret.hr.hrHeadImg or const.HR_HEADIMG),
                deleted=ret.hr.isDelete
            )

        mobot_conf_data = yield self.infra_company_ds.get_company_mobot_conf(company_id)
        if mobot_conf_data.get('data'):
            mobot_conf = mobot_conf_data.get('data')
            mobot_info.name = mobot_conf['mobot_head_img'] or "小助手"
            mobot_info.headimg = make_static_url(mobot_conf['mobot_head_img'] or const.HR_HEADIMG)

        user_info = ObjectDict()
        if ret.user:
            user_info = ObjectDict(
                user_id=ret.user.userId,
                user_name=ret.user.userName,
                user_headimg=make_static_url(ret.user.userHeadImg or const.SYSUSER_HEADIMG)
            )

        position_info = ObjectDict()
        if ret.position:
            position_info = ObjectDict(
                pid=ret.position.positionId,
                title=ret.position.positionTitle,
                company_name=ret.position.companyName,
                city=ret.position.city,
                salary=gen_salary(ret.position.salaryTop, ret.position.salaryBottom),
                update=str_2_date(ret.position.updateTime, const.TIME_FORMAT_MINUTE),
                status=ret.position.status,
                team=ret.position.team
            )
        res = ObjectDict(
            hr=hr_info,
            mobot=mobot_info,
            user=user_info,
            position=position_info,
            chat_debut=ret.chatDebut,
            follow_qx=qxuser.is_subscribe == 1,
            room_id=ret.roomId,
            show_position_info=(len(position_info) > 0 and not mobot_enable),
            recom=recom,
            is_employee=is_employee
        )
        raise gen.Return(res)

    @gen.coroutine
    def leave_chatroom(self, room_id, speaker=0):
        """
        离开聊天室
        :param room_id:
        :param speaker: 0：求职者，1：HR
        :return:
        """

        ret = yield self.thrift_chat_ds.leave_chatroom(room_id, speaker)
        raise gen.Return(ret)

    @gen.coroutine
    def save_chat(self, params):
        """
        记录聊天内容
        :param params:
        :return:
        """

        ret = yield self.thrift_chat_ds.save_chat(params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_chatroom_info(self, room_id):

        """返回JD 页，求职者与 HR 之间的未读消息数"""
        chatroom = yield self.hr_wx_hr_chat_list_ds.get_chatroom(conds={
            "id": int(room_id),
        })

        raise gen.Return(chatroom)

    @gen.coroutine
    def get_unread_chat_num(self, user_id, hr_id):
        """返回JD 页，求职者与 HR 之间的未读消息数"""

        if user_id is None or not hr_id:
            raise gen.Return(1)

        chatroom = yield self.hr_wx_hr_chat_list_ds.get_chatroom(conds={
            "hraccount_id": int(hr_id),
            "sysuser_id": user_id
        })

        # 若无聊天，则默认显示1条未读消息
        if not chatroom:
            raise gen.Return(1)

        raise gen.Return(chatroom.user_unread_count)

    @gen.coroutine
    def get_all_unread_chat_num(self, user_id):

        """返回求职者所有的未读消息数，供侧边栏我的消息未读消息提示"""

        if user_id is None:
            raise gen.Return(0)

        unread_count_total = yield self.hr_wx_hr_chat_list_ds.get_chat_unread_count_sum(conds={
            "sysuser_id": user_id,
        }, fields=["user_unread_count"])
        if unread_count_total is None:
            return gen.Return(0)
        raise gen.Return(unread_count_total.sum_user_unread_count)

    @gen.coroutine
    def get_hr_info(self, publisher):
        """获取 hr 信息"""
        hr_account = yield self.user_hr_account_ds.get_hr_account({
            "id": publisher
        })

        raise gen.Return(hr_account)

    @gen.coroutine
    def get_company_conf(self, company_id):
        """获取公司信息"""
        company_conf = yield self.hr_company_conf_ds.get_company_conf(
            conds={'company_id': company_id})

        raise gen.Return(company_conf)

    @log_time
    @gen.coroutine
    def infra_clound_get_position_list_rp_ext(self, pids):
        """获取职位的红包信息"""
        if not pids:
            raise gen.Return([])

        params = [("positionIdList", pid) for pid in pids]  # todo get方法加list参数，先这样处理下，重构的时候再优雅的解决
        res = yield self.infra_position_ds.get_position_list_rp_ext(params)
        if res.code == const.NEWINFRA_API_SUCCESS and res.data:
            raise gen.Return([ObjectDict(e) for e in res.data])

        raise gen.Return([])

    @log_time
    @gen.coroutine
    def infra_clound_get_position_list(self, params, is_employee, banner):
        """
        根据pids获取职位列表

        :param params: ['1', '2', '3'] 职位ID的str列表
        :param banner: [] 公司banner数组数据，current_user.company.banner

        """

        def get_rpext(rpext_list, pid):
            rpext = [e for e in rpext_list if e.pid == pid]
            return rpext[0] if rpext else ObjectDict()

        if not params:
            raise gen.Return([])

        rpext_list = yield self.infra_clound_get_position_list_rp_ext(params)

        pids = ','.join(params)
        res = yield self.infra_position_ds.get_position_list_by_pids({'pids': pids})

        tmp_position = {}
        if res.code == const.NEWINFRA_API_SUCCESS and res.data:
            for data in res.data:
                position_info = ObjectDict(data.get('position', {}) or {})
                company_info = ObjectDict(data.get('company', {}) or {})
                team_info = ObjectDict(data.get('team', {}) or {})
                rpext = get_rpext(rpext_list, position_info.id)

                position = ObjectDict()
                position.jobTitle = position_info.title
                position.company = company_info.abbreviation
                position.team = team_info.name
                position.salary = position_info.salary
                position.location = position_info.city
                position.update = position_info.update_time
                position.id = position_info.id
                position.imgUrl = banner
                position.cover = make_static_url(company_info.logo)  # TODO 如果有红包或其他特殊场景的cover设置

                # 前端显示红包的逻辑为 hb_status True 就显示红包样式
                # employeeOnly true 员工可见，false 粉丝可见
                if rpext:
                    # 员工可见
                    if is_employee:
                        position.hb_status = True

                    # 粉丝可见
                    elif not rpext.employeeOnly:
                        position.hb_status = True

                    # 员工或粉丝不可见
                    else:
                        position.hb_status = False
                else:
                    position.hb_status = False

                tmp_position.update({str(position_info.id): position})

        # 处理排序
        position_list = []
        for pid in params:
            position_list.append(tmp_position.get(pid))

        raise gen.Return(position_list)

    @gen.coroutine
    def get_fast_entry(self, company_id):
        uri = 'company/{company_id}/fastentry/config'.format(company_id=company_id)
        route = '{host}{uri}'.format(host=settings['chatbot_host'], uri=uri)
        result = yield http_get(route=route, jdata=None, infra=False, timeout=1)
        raise gen.Return(result)

    @gen.coroutine
    def get_chatbot_reply(self, message, user_id, hr_id, position_id, flag, social, campus, create_new_context,
                          current_user,
                          from_textfield):
        """ 调用 chatbot 返回机器人的回复信息
               https://wiki.moseeker.com/chatbot.md
        :param message: 用户发送到文本内容
        :param user_id: 当前用户id
        :param hr_id: 聊天对象hrid
        :param position_id 当前职位id，不存在则为0
        :param flag: 0:社招 1:校招 2:meet mobot 3: 智能推荐
        :param create_new_context: meet mobot标识
        :param current_user:
        :param from_textfield:
        :param social:社招判断开关 1：开启；
        :param campus:校招判断开关 1：开启；
        """
        messages = []

        params = ObjectDict(
            question=message,
            user_id=user_id,
            hr_id=hr_id,
            position_id=position_id,
            create_new_context=create_new_context,
            from_textfield=from_textfield
        )
        self.logger.debug("get_chatbot_reply==>create_new_context:{} ".format(create_new_context))
        self.logger.debug("chabot_params:flag:%s, social:%s, capmpus:%s" % (flag, social, campus))
        self.logger.debug("chabot_params type :flag:%s, social:%s, capmpus:%s"
                          % (type(flag), type(social), type(campus)))
        flag = int(flag) if flag else None
        try:
            if flag == 1:
                res = yield http_post(
                    route='{host}{uri}'.format(host=settings['chatbot_host'], uri='campus_qa.api'), jdata=params,
                    infra=False)
            elif flag is None and social == 0 and campus == 1:
                res = yield http_post(
                    route='{host}{uri}'.format(host=settings['chatbot_host'], uri='campus_qa.api'), jdata=params,
                    infra=False)
            else:
                res = yield http_post(
                    route='{host}{uri}'.format(host=settings['chatbot_host'], uri='qa.api'), jdata=params,
                    infra=False)

            self.logger.debug(res.results)
            results = res.results
            for r in results:
                ret_message = yield self.make_response(r, current_user)
                messages.append(ret_message)
            self.logger.debug(messages)
        except Exception as e:
            self.logger.error("[get_chatbot_reply_fail!!]reeor: %s, params: %s" % (e, params))
            return []
        else:
            return messages

    @gen.coroutine
    def make_response(self, message, current_user):
        """
        对chatbot的部分消息类型做整理
        """
        is_employee = bool(current_user.employee if current_user else None)

        ids = []
        res_type = message.get("resultType", "")
        ret = message.get("values", {})
        content = ret.get("content", "")
        compoundContent = ret.get("compoundContent") or {}
        stats = ret.get("stats") or {}
        msg_type = const.MSG_TYPE.get(res_type)
        ret_message = ObjectDict()
        ret_message['content'] = content
        ret_message['compound_content'] = compoundContent
        ret_message['msg_type'] = msg_type
        ret_message['stats'] = stats

        if msg_type == "citySelect":
            max = ret_message['compound_content'].get("max")
            ret_message['compound_content'] = ObjectDict()  # 置空compoundContent
            cities = compoundContent.get("list")
            hot, list = self.order_country_by_first_letter(cities)
            ret_message['compound_content']['list'] = list
            ret_message['compound_content']['hot'] = hot
            ret_message['compound_content']['max'] = max

        if msg_type == "jobCard":
            ids = [str(p.get("id")) for p in compoundContent]
            positions = yield self.infra_clound_get_position_list(ids, is_employee, current_user.company.banner)
            ret_message['compound_content'] = ObjectDict(list=positions)

        if msg_type == "jobSelect":
            ids = [str(p.get("id")) for p in compoundContent.get("list")]
            positions = yield self.infra_clound_get_position_list(ids, is_employee, current_user.company.banner)
            ret_message['compound_content']['list'] = positions

        return ret_message

    @staticmethod
    def order_country_by_first_letter(cities):
        hot_cities = list(filter(
            lambda x: x.get('hot_city') is True, cities))
        res, heads = [], []
        for el in cities:
            h = lazy_pinyin(
                el.get('name'),
                style=pypinyin.STYLE_FIRST_LETTER)[0].upper()

            if h not in heads:
                cities_group = ObjectDict(text=h, list=[])
                cities_group.list.append(ObjectDict(el))
                res.append(cities_group)
                heads.append(h)
            else:
                group = list(filter(lambda x: x.text == h, res))[0]
                group.list.append(el)

        ret = sorted(res, key=lambda x: x.text)

        return hot_cities, ret

    @gen.coroutine
    def chat_limit(self, hr_id):
        """
        对聊天方式做限制
        """
        params = ObjectDict({
            "hrId": hr_id
        })
        ret = yield self.thrift_chat_ds.chat_limit(params)
        status = ret.get("status")
        msg = ret.get("message")
        return status, msg

    @gen.coroutine
    def get_voice(self, user_id, hr_id, room_id, server_id):
        """
        获取语音文件
        :param user_id:
        :param hr_id:
        :param room_id:
        :param server_id:
        :return:
        """
        params = ObjectDict({
            "userId": user_id,
            "hrId": hr_id,
            "roomId": room_id,
            "serverId": server_id
        })
        ret = yield self.thrift_chat_ds.get_voice(params)
        return ret

    @gen.coroutine
    def get_company_hr_info(self, hr_id=0):
        """
        获取HR账号信息
        """
        hr_info_data = ObjectDict()

        if hr_id == 0:
            raise gen.Return(hr_info_data)

        params = {"hrId": hr_id}
        hr_info = yield self.infra_company_ds.get_company_hr_info(params)
        if hr_info.get('data'):
            hr_info_data = ObjectDict(hr_info.get('data'))

        raise gen.Return(hr_info_data)

    @gen.coroutine
    def get_mobot_hosting_status(self, hr_id):
        """
        获取HR后台对MoBot的托管状态
        :return: True 托管 False 未托管
        """
        hr_info = yield self.get_company_hr_info(hr_id)
        # HR聊天是否托管给智能招聘助手，0 不托管，1 托管
        mobot_enable = bool(hr_info.leave_to_mobot) if hr_info else False
        raise gen.Return(mobot_enable)
