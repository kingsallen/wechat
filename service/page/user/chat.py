# coding=utf-8
import datetime
from tornado import gen

import conf.common as const
import conf.path as path
from service.page.base import PageService
from service.page.job.position import PositionPageService
from service.page.hr.team import TeamPageService
from service.page.hr.company import CompanyPageService
from setting import settings
from util.common import ObjectDict
from util.tool.date_tool import str_2_date, curr_now_minute
from util.tool.http_tool import http_post
from util.tool.str_tool import gen_salary
from util.tool.url_tool import make_static_url, make_url
import json
import pypinyin
from pypinyin import lazy_pinyin


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
    def get_chatroom(self, user_id, hr_id, company_id, position_id, room_id, qxuser, is_gamma, bot_enabled):
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
            if bot_enabled:
                data = (yield self.infra_company_ds.get_company_mobot_image(company_id))['data']
                if data['mobot_head_img']:
                    hr_info['hr_headimg'] = data['mobot_head_img']
                if data['mobot_name']:
                    hr_info['hr_name'] = data['mobot_name']

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
            show_position_info=(len(position_info) > 0 and not bot_enabled)
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
    def get_chatbot_reply(self, message, user_id, hr_id, position_id, flag, social, campus, create_new_context, current_user,
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
        self.logger.debug("chabot_params:flag:%s, social:%s, capmpus:%s"%(flag, social, campus))
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

        @gen.coroutine
        def get_position_list(ids):
            position_list = []
            position_ps = PositionPageService()
            team_ps = TeamPageService()
            company_ps = CompanyPageService()
            for id in ids:
                position_info = yield position_ps.get_position(id)  # todo 这个方法并不适合批量拼装职位详情，现在chatbot最多十个职位，故暂时借用该方法。
                jd_position = yield position_ps.get_cms_page(position_info.team_id)
                team = yield team_ps.get_team_by_id(position_info.team_id)
                did = yield company_ps.get_real_company_id(position_info.publisher, position_info.company_id)
                p_company_info = yield company_ps.get_company(conds={"id": current_user.company.id}, need_conf=True)
                company_info = yield company_ps.get_company(conds={"id": did}, need_conf=True)
                position = ObjectDict()
                position.jobTitle = position_info.title
                position.hb_status = position_info.hb_status
                position.company = company_info.abbreviation
                position.team = team.name
                position.salary = position_info.salary
                position.location = position_info.city
                position.update = position_info.update_time
                position.id = position_info.id
                position.imgUrl = p_company_info.banner
                if team:
                    teamname_custom = current_user.company.conf_teamname_custom
                    more_link = team.link if team.link else make_url(path.TEAM_PATH.format(team.id),
                                                                     wechat_signature=current_user.wechat.signature)
                    team_des = yield position_ps.get_team_data(team, more_link, teamname_custom)
                    if team_des:
                        for item in team_des['data']:
                            if item and item.get('media_url') and item.get('media_type') == 'image':
                                position.imgUrl = item.get('media_url')
                                if position.imgUrl:
                                    break
                elif jd_position:
                    for item in jd_position['data']:
                        if item and item.get('media_url') and item.get('media_type') == 'image':
                            position.imgUrl = item.get('media_url')
                            if position.imgUrl:
                                break
                position_list.append(position)
            return position_list

        if msg_type == "jobCard":
            ids = [p.get("id") for p in compoundContent]
            positions = yield get_position_list(ids)
            ret_message['compound_content'] = ObjectDict(list=positions)
        if msg_type == "jobSelect":
            ids = [p.get("id") for p in compoundContent.get("list")]
            positions = yield get_position_list(ids)
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
