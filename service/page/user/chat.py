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
    def get_user_chatroom_page(self, user_id, page_no, page_size):
        """获得聊天室列表"""

        def get_hr_info(hrs, hr_id):
            for h in hrs:
                if h['id'] == hr_id:
                    return ObjectDict(h)

        def get_company_info(companys, company_id):
            for c in companys:
                if c['id'] == company_id:
                    return ObjectDict(c)

        records = []
        hr_ids = []
        company_ids = []

        user_chatroom_page = yield self.infra_immobot_ds.get_user_chatroom_page(user_id, page_no, page_size)
        self.logger.debug(user_chatroom_page)

        if not user_chatroom_page.data.current_page_data:
            raise gen.Return(records)

        # 过滤hr_ids
        for r in user_chatroom_page.data.current_page_data:
            r = ObjectDict(r)
            if r.hr_id not in hr_ids:
                hr_ids.append(r.hr_id)

        # 根据hrids批量获取hr信息
        company_hr_list = yield self.infra_company_ds.get_company_hr_list(hr_ids)
        if not company_hr_list.data:
            self.logger.error("get_user_chatroom_page get_company_hr_list error, hr_ids:{}".format(hr_ids))
            raise gen.Return(records)

        # 过滤company_ids
        for hr in company_hr_list.data:
            hr = ObjectDict(hr)
            if hr.company_id not in company_ids:
                company_ids.append(hr.company_id)

        # 根据company_ids批量获取公司信息
        company_list = yield self.infra_company_ds.get_company_list(company_ids)
        if not company_list.data:
            self.logger.error("get_user_chatroom_page get_company_list error, company_ids:{}".format(company_ids))
            raise gen.Return(records)

        for d in user_chatroom_page.data.current_page_data:
            d = ObjectDict(d)
            hr = get_hr_info(company_hr_list.data, d.hr_id)
            company = get_company_info(company_list.data, hr['company_id'])
            if not hr or not company:
                self.logger.warning("get_user_chatroom_page hr or company not exist, hr_id:{}".format(d.hr_id))
                continue

            room = ObjectDict()
            room['id'] = d.room_id
            room['hr_id'] = d.hr_id
            room['hr_name'] = hr.username or "HR"
            room['hr_headimg'] = make_static_url(hr.headimgurl or company.logo or const.HR_HEADIMG)
            room['company_name'] = company.abbreviation or company.name or ""
            room['chat_time'] = str_2_date(d.update_time, self.constant.TIME_FORMAT_MINUTE)
            room['unread_num'] = d.user_have_unread_msg
            records.append(room)

        raise gen.Return(records)

    @gen.coroutine
    def get_user_chat_history_record_page(self, room_id, user_id, page_no, page_size):
        """获取用户聊天历史记录分页数据"""
        records = []
        user_chat_history_record_page = yield self.infra_immobot_ds.get_user_chat_history_record_page(
            room_id, user_id, page_no, page_size)

        # IM37006 数据权限校验失败
        if user_chat_history_record_page.code != '0':
            raise gen.Return(user_chat_history_record_page.code)

        if not user_chat_history_record_page.data.current_page_data:
            raise gen.Return(records)

        for c in user_chat_history_record_page.data.current_page_data:
            c = ObjectDict(c)
            if c.msg_type == 'voice':
                compound_content = dict(duration=c.duration, server_id=c.server_id, asset_url=c.local_url)
            else:
                compound_content = json.loads(c.compound_content if c.compound_content else '{}') or {}

            stats = json.loads(c.stats if c.stats else '{}') or {}

            chat = ObjectDict()
            chat['id'] = c.id
            chat['content'] = c.content or ''
            chat['chatTime'] = str_2_date(c.create_time, const.TIME_FORMAT)
            chat['speaker'] = c.speaker  # 0：求职者，1：HR
            chat['msgType'] = c.msg_type
            chat['compoundContent'] = compound_content
            chat['stats'] = stats
            records.append(chat)

        raise gen.Return(records)

    @gen.coroutine
    def get_chatroom(self, sysuser, hr_id, position_id, room_id, qxuser, is_gamma, mobot_enable, recom, is_employee):
        """进入聊天室"""
        hr_info = ObjectDict()
        mobot_info = ObjectDict(enable=mobot_enable, name='', headimg='')

        user_info = ObjectDict(
            user_id=sysuser.id,
            user_name=sysuser.name,
            user_headimg=make_static_url(sysuser.headimg or const.SYSUSER_HEADIMG)
        )
        ret = yield self.infra_immobot_ds.user_enter_chatroom(room_id, sysuser.id, hr_id, position_id, is_gamma)
        if not ret.data:
            raise gen.Return("")

        room = ObjectDict(ret.data)
        if room.hr_account:
            hr_account = ObjectDict(room.hr_account)
            hr_info = ObjectDict(
                hr_id=hr_account.id,
                hr_name=hr_account.username or "HR",
                hr_headimg=make_static_url(hr_account.headimgurl or const.HR_HEADIMG),
                deleted=(hr_account.disable == 0)
            )

        if room.company_conf:
            company_conf = ObjectDict(room.company_conf)
            mobot_info.name = company_conf.mobot_name or "小助手"
            mobot_info.headimg = make_static_url(company_conf.mobot_head_img or hr_info.hr_headimg or const.HR_HEADIMG)

        position_info = ObjectDict()
        if room.position:
            full_position = ObjectDict(room.position)
            position = ObjectDict(full_position.position) if full_position.position else ObjectDict()
            company = ObjectDict(full_position.company) if full_position.company else ObjectDict()
            team = ObjectDict(full_position.team) if full_position.team else ObjectDict()
            salary = ObjectDict(full_position.salary_data) if full_position.salary_data else ObjectDict()
            team_name = team.name if team else position.department

            position_info = ObjectDict(
                pid=position.id,
                title=position.title,
                company_name=company.name,
                city=ret.position.city,
                salary=gen_salary(salary.salary_top, salary.salary_bottom),
                update=str_2_date(position.update_time, const.TIME_FORMAT_MINUTE),
                status=position.status,
                team=team_name
            )
        res = ObjectDict(
            hr=hr_info,
            mobot=mobot_info,
            user=user_info,
            position=position_info,
            chat_debut=room.is_new_created,
            follow_qx=qxuser.is_subscribe == 1,
            room_id=room.room_id,
            show_position_info=(len(position_info) > 0 and not mobot_enable),
            recom=recom,
            is_employee=is_employee
        )
        raise gen.Return(res)

    @gen.coroutine
    def leave_chatroom(self, room_id, user_id, speaker=0):
        """
        离开聊天室
        :param speaker: 0：求职者，1：HR
        :return:
        """
        ret = yield self.infra_immobot_ds.user_leave_chatroom(room_id, user_id, speaker)
        raise gen.Return(ret)

    @gen.coroutine
    def save_chat(self, company_id, room_id, user_id, msg_type, origin, pid, content, compound_content, speaker,
                  voice_server_id, voice_duration):
        """
        保存聊天记录
        """
        ret = yield self.infra_immobot_ds.save_chat_record(company_id, room_id, user_id, msg_type, origin, pid, content,
                                                           compound_content, speaker, voice_server_id, voice_duration)
        if not ret.data:
            raise gen.Return({})

        raise gen.Return(ret.data)

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
        result = yield http_get(route=route, jdata=None, infra=False, timeout=5)
        raise gen.Return(result)

    @gen.coroutine
    def get_chatbot_reply(self, message, user_id, hr_id, position_id, flag, social, campus, create_new_context,
                          current_user, from_textfield, project_id):
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
        :param project_id: MoPlan预约项目ID
        """
        messages = []

        params = ObjectDict(
            question=message,
            user_id=user_id,
            hr_id=hr_id,
            position_id=position_id,
            create_new_context=create_new_context,
            from_textfield=from_textfield,
            project_id=project_id
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

            self.logger.debug(res)
            if res.status == 0 and res.data.results:
                results = res.data.results
                for r in results:
                    ret_message = yield self.make_response(r, current_user)
                    messages.append(ret_message)
        except Exception as e:
            self.logger.error("mobot api error: %s, params: %s" % (e, params))
            # 回复默认信息
            default_message = dict(resultType=0,
                                   resultTypeName='html',
                                   values=dict(content='很抱歉，HR小姐姐还没告诉我答案，我暂时不能帮你回答问题哦。',
                                               compoundContent=None))
            default_result_message = yield self.make_response(default_message, current_user)
            messages.append(default_result_message)

        self.logger.debug(messages)
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
        msg_type = message.get("resultTypeName")
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
        if hr_info.data:
            hr_info_data = ObjectDict(hr_info.data)

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
