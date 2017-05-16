# coding=utf-8

# @Time    : 4/13/17 11:42
# @Author  : panda (panyuxin@moseeker.com)
# @File    : position.py
# @DES     : 聚合号职位详情页

import random
from tornado import gen

import conf.path as path
from handler.base import BaseHandler
from util.common.decorator import handle_response
from util.common import ObjectDict
from util.tool.str_tool import split, add_item


class PositionHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self, position_id):

        position_info = yield self.position_ps.get_position(position_id)

        self.logger.debug("[JD]构建职位所属公司信息")
        did = yield self.company_ps.get_real_company_id(position_info.publisher, position_info.company_id)
        company_info = yield self.company_ps.get_company(conds={"id": did}, need_conf=True)

        self.logger.debug("position:{}".format(position_info))
        self.logger.debug("company:{}".format(company_info))

        if position_info.id and company_info.conf_show_in_qx != 0:
            self.logger.debug("[JD]构建职位默认图")
            position_es = yield self.aggregation_ps.opt_es_position(position_info.id)
            pos_item = position_es.hits.hits[0] if position_es.hits.hits else ObjectDict()

            self.logger.debug("[JD]构建职位基础信息")
            res_position, cover = yield self._make_jd_info(position_info, company_info, pos_item)

            self.logger.debug("[JD]构建职位详情信息")
            jd_detail = yield self._make_jd_detail(position_info, pos_item)

            self.logger.debug("[JD]构建公司信息")
            res_cmp = self._make_company(company_info)

            self.logger.debug("[JD]构建转发信息")
            res_share = yield self._make_share_info(position_info, company_info, position_es)

            self.send_json_success(data=ObjectDict(
                position=res_position,
                company=res_cmp,
                share=res_share,
                modules=jd_detail,
                cover=cover,
            ))

            # 标记用户已阅读职位
            self.logger.debug("[JD]标记用户已阅读职位")
            yield self.user_ps.add_user_viewed_position(self.current_user.sysuser.id, position_info.id)
        else:
            self.send_json_error()
            return

    def _make_company(self, company_info):
        """
        构造公司信息
        :param company_info:
        :return:
        """

        default = ObjectDict(
            id=company_info.id,
            abbreviation=company_info.abbreviation,
            name=company_info.name,
            logo=self.static_url(company_info.logo),
            description=company_info.introduction,
        )

        return default

    @gen.coroutine
    def _make_jd_info(self, position_info, company_info, pos_item):

        team_img, job_img, company_img = yield self.aggregation_ps.opt_jd_home_img(pos_item)

        self.logger.debug("[JD]构建收藏信息")
        star = yield self.position_ps.is_position_stared_by(self.current_user.sysuser.id, position_info.id)

        self.logger.debug("[JD]构建申请信息")
        application = yield self.application_ps.get_application(position_info.id, self.current_user.sysuser.id)

        # 是否超出投递上限。每月每家公司一个人只能申请3次
        self.logger.debug("[JD]处理投递上限")
        can_apply = yield self.application_ps.is_allowed_apply_position(
            self.current_user.sysuser.id, company_info.id)

        if company_info.conf_newjd_status != 2:
            # 未采用新 JD
            cover = company_info.banner[0] if company_info.banner else job_img
        else:
            cover = job_img

        position = ObjectDict(
            id=position_info.id,
            title=position_info.title,
            status=position_info.status,
            salary=position_info.salary,
            team=pos_item.get("_source", {}).get("team",{}).get("name", ""),
            team_id=pos_item.get("_source", {}).get("team",{}).get("id", 0),
            city=split(position_info.city, [",","，"]),
            degree=position_info.degree,
            experience=position_info.experience,
            team_img=team_img,
            job_img=job_img,
            company_img=company_img,
            is_applied=bool(application),
            appid=application.id or 0,
            is_collected=star,
            can_apply=not can_apply,
            hr_chat=int(company_info.conf_hr_chat),
        )

        return position, cover

    @gen.coroutine
    def _make_jd_detail(self, position_info, pos_item):
        """
        构造职位的 module 信息
        :param position_info:
        :return:
        """

        position_temp = ObjectDict()
        module_job_description = self.__make_json_job_description(position_info)
        module_job_need = self.__make_json_job_need(position_info)
        module_feature = self.__make_json_job_feature(position_info)
        module_job_require = self.__make_json_job_require(position_info, pos_item)

        add_item(position_temp, "module_job_description", module_job_description)
        add_item(position_temp, "module_job_need", module_job_need)
        add_item(position_temp, "module_feature", module_feature)
        add_item(position_temp, "module_job_require", module_job_require)

        return position_temp

    def __make_json_job_description(self, position_info):
        """构造职位描述"""
        if not position_info.accountabilities:
            data = None
        else:
            data = ObjectDict({
                "data": position_info.accountabilities,
            })

        return data

    def __make_json_job_require(self, position_info, pos_item):
        """构造职位要求"""
        require = []

        if pos_item.get("_source", {}).get("team",{}).get("name", ""):
            require.append(ObjectDict(name="所属部门", value=pos_item.get("_source", {}).get("team",{}).get("name", "")))
        if position_info.experience:
            require.append(ObjectDict(name="工作性质", value=position_info.employment_type))
        if position_info.language:
            require.append(ObjectDict(name="语言要求", value=position_info.language))

        if len(require) == 0:
            data = None
        else:
            data = ObjectDict({
                "data": require
            })
        return data

    def __make_json_job_feature(self, position_info):
        """构造职位福利特色"""
        if not position_info.feature:
            data = None
        else:
            data = ObjectDict({
                "data": position_info.feature,
            })

        return data

    def __make_json_job_need(self, position_info):
        """构造职位要求"""

        if not position_info.requirement:
            data = None
        else:
            data = ObjectDict({
                "data": position_info.requirement,
            })

        return data

    @gen.coroutine
    def _make_share_info(self, position_info, company_info, pos_item):
        """构建 share 内容"""

        cover = self.__make_share_info_cover(pos_item, company_info)
        title = "【{}】-{}正在寻求你的加入".format(position_info.title, company_info.abbreviation)
        description = "微信好友{}推荐，{}{}正在寻找{}的合适人选，等的就是你！".format(self.current_user.qxuser.nickname,
                                                                company_info.abbreviation,
                                                                "的{}".format(pos_item.get("_source", {}).get("team",{}).get("name", "")) if pos_item.get("_source", {}).get("team",{}) else "",
                                                                position_info.title)

        link = self.make_url(
            path.GAMMA_POSITION_JD.format(position_info.id),
            self.params,
            recom=self.position_ps._make_recom(self.current_user.sysuser.id),
            fr="recruit",
            did=str(company_info.id)
        )

        share = ObjectDict({
            "cover": cover,
            "title": title,
            "description": description,
            "link": link,
        })

        return share

    def __make_share_info_cover(self, pos_item, company_info):
        """
        构造分享的 cover
        有新JD的，在本职位所属团队的团队图片、职位图片里面随机选取；没有新JD的，选取公司头图、企业印象三张图随机选取
        :param pos_item:
        :param company_info:
        :return:
        """
        pic_list = list()
        cover_str = self.static_url(company_info.logo)
        if company_info.conf_newjd_status != 2:
            # 为采用新 JD
            pic_list += company_info.impression
            pic_list += company_info.banner
        else:
            pic_list_res = list()
            if pos_item.get("_source", {}).get("jd_pic",{}).get("position_pic"):
                pic_list_res += pos_item.get("_source", {}).get("jd_pic",{}).get("position_pic")
            if pos_item.get("_source", {}).get("jd_pic",{}).get("team_pic"):
                pic_list_res += pos_item.get("_source", {}).get("jd_pic",{}).get("team_pic")

            for item in pic_list_res:
                pic_list.append(self.static_url(item['res_url']))

        if len(pic_list) > 0:
            res_resource = random.sample(pic_list, 1)
            cover_str = res_resource[0]

        return cover_str

class PositionRecommendHandler(BaseHandler):
    """JD页，公司主页职位推荐"""

    @handle_response
    @gen.coroutine
    def get(self, id):

        page_no = self.params.page_no or 1

        hot_positions = ObjectDict()
        if self.params.is_pos:
            # 职位详情页相似职位
            hot_positions = yield self._make_pos_positions(id, page_no)

        elif self.params.is_cmp:
            hot_positions = yield self._make_cmp_positions(id, page_no)

        self.send_json_success(data=hot_positions)

    @gen.coroutine
    def _make_pos_positions(self, position_id, page_no):
        """处理JD 页相似职位推荐"""

        ret = yield self.position_ps.get_position_positions(position_id, page_no)

        default = ObjectDict(
            title="相似职位",
            data=ret
        )
        return default

    @gen.coroutine
    def _make_cmp_positions(self, company_id, page_no):
        """
        构造该企业热招职位
        :param company_id:
        :return:
        """

        ret = yield self.company_ps.get_company_positions(company_id, page_no)

        default = ObjectDict(
            title="该企业热招职位",
            data=ret
        )

        return default
