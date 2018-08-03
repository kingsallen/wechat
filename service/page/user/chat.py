# coding=utf-8
import datetime
from tornado import gen

import conf.common as const
from service.page.base import PageService
from setting import settings
from util.common import ObjectDict
from util.tool.date_tool import str_2_date, curr_now_minute
from util.tool.http_tool import http_post
from util.tool.str_tool import gen_salary
from util.tool.url_tool import make_static_url
import json


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
                room['content'] = '' if e.msgType == "job" else e.content  # 之前job类型用了content作为json存储了，现在兼容到compoundContent中去
                room['chatTime'] = str_2_date(e.createTime, const.TIME_FORMAT_MINUTE)
                room['speaker'] = e.speaker  # 0：求职者，1：HR
                room['msgType'] = e.msgType
                room['compoundContent'] = json.loads(e.content) if e.msgType == "job" and e.content else json.loads(e.compoundContent)
                obj_list.append(room)
            last_msg = obj_list[-1]
            last_time = str_2_date(last_msg.chatTime, "%Y-%m-%d %H:%M:%S")

            now = curr_now_minute()
            delta = datetime.timedelta(minutes=14)  # chatbot15分钟会跳出流程，这里做下校验，给用户一分钟操作的时间
            delta_data = now + delta
            n = delta_data.strftime("%Y-%m-%d %H:%M:%S")
            delta_time = str_2_date(n, "%Y-%m-%d %H:%M:%S")
            is_expire = delta_time > last_time
            if last_msg.msgType in const.INTERACTIVE_MSG and is_expire:
                last_msg.compoundContent['disabled'] = False

        raise gen.Return(obj_list)

    @gen.coroutine
    def get_chatroom(self, user_id, hr_id, position_id, room_id, qxuser, is_gamma):
        """进入聊天室"""

        ret = yield self.thrift_chat_ds.enter_chatroom(user_id, hr_id, position_id, room_id, is_gamma)

        hr_info = ObjectDict()
        if ret.hr:
            hr_info = ObjectDict(
                hr_id=ret.hr.hrId,
                hr_name=ret.hr.hrName or "HR",
                hr_headimg=make_static_url(ret.hr.hrHeadImg or const.HR_HEADIMG),
                deleted=ret.hr.isDelete
            )

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
            user=user_info,
            position=position_info,
            chat_debut=ret.chatDebut,
            follow_qx=qxuser.is_subscribe == 1,
            room_id=ret.roomId,
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

    @gen.coroutine
    def get_chatbot_reply(self, message, user_id, hr_id, position_id):
        """ 调用 chatbot 返回机器人的回复信息
               https://wiki.moseeker.com/chatbot.md
        :param message: 用户发送到文本内容
        :param user_id: 当前用户id
        :param hr_id: 聊天对象hrid
        :param position_id 当前职位id，不存在则为0
        """
        messages = []

        params = ObjectDict(
            question=message,
            user_id=user_id,
            hr_id=hr_id,
            position_id=position_id
        )

        try:
            res = yield http_post(
                route=settings['chatbot_api'], jdata=params, infra=False)

            self.logger.debug("[get_chatbot_reply]ret: %s, type: %s" % (res, type(res)))

            self.logger.debug(res.results)
            results = res.results
            for r in results:
                ret_message = self.make_response(r)
                messages.append(ret_message)
            self.logger.debug(messages)
        except Exception as e:
            self.logger.error(e)
            return
        else:
            return messages

    def make_response(self, message):
        """
        对chatbot的部分消息类型做整理
        """
        ids = []
        res_type = message.get("resultType", "")
        ret = message.get("values", {})
        content = ret.get("content", "")
        compoundContent = ret.get("compoundContent", {})
        msg_type = const.MSG_TYPE.get(res_type)
        ret_message = ObjectDict()
        ret_message['content'] = content
        ret_message['compound_content'] = compoundContent
        ret_message['msg_type'] = msg_type
        if msg_type == "jobCard":
            ids = [p.get("id") for p in compoundContent]
        if msg_type == "jobSelect":
            ids = [p.get("id") for p in compoundContent.get("list")]
        if ids:
            max = ret_message['compoundContent'].get("max")
            ret_message['compoundContent'] = ObjectDict()  # 置空compoundContent
            position_list = []
            position_info = ObjectDict()
            positions = yield self.infra_position_ds.get_positions_by_ids(ids)
            for p in positions:
                position_info['jobTitle'] = p.title
                position_info['company'] = p.title
                position_info['team'] = p.title
                position_info['location'] = p.title
                position_info['salary'] = p.title
                position_info['update'] = p.title
                position_info['id'] = p.title
                position_list.append(position_info)
            ret_message['compoundContent']['list'] = position_list
            if max:
                ret_message['compoundContent']['max'] = max
        return ret_message

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


