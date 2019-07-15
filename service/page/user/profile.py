# coding=utf-8

import re
from datetime import datetime

import tornado.gen as gen
from tornado.escape import json_decode, json_encode

import conf.common as const
import conf.infra as infra_const
from service.page.base import PageService
from util.common import ObjectDict
from util.tool.dict_tool import sub_dict, rename_keys
from util.tool.iter_tool import first
from globals import env
from conf.locale_dict import CITY, CITY_REVERSE, INDUSTRY, INDUSTRY_REVERSE
import json
import conf.path as path
import hashlib
from urllib.parse import urlencode
from util.common.cache import BaseRedis
from service.page.hr.company import CompanyPageService
from service.page.job.position import PositionPageService
from service.page.user.privacy import PrivacyPageService

class ProfilePageService(PageService):
    """对接profile服务
    referer: https://wiki.moseeker.com/profile-api.md
    """

    FE_ROUTES = ObjectDict({
        "basic": "basic",
        "description": "basic",
        "jobexp": "workexp",
        "projectexp": "projectexp",
        "jobpref": "intention",
        "language": "language",
        "skill": "skill",
        "cert": "credentials",
        "link": "works",
        "prize": "awards",
        "eduexp": "education",
        "jobexp_company": "jobexp_company"
    })

    BASIC_KEYS = [
        'name', 'birth', 'city_name', 'gender', 'motto', 'self_introduction',
        'profile_id', 'nationality_name', 'nationality_code'
    ]

    LANGUAGE_KEYS = [
        'id', 'name', 'level'
    ]

    CERT_KEYS = SKILL_KEYS = [
        'id', 'name'
    ]

    WORKEXP_KEYS = [
        "id", "start_date", "end_date", "end_until_now", "department_name",
        "job", "description", "company_name"
    ]

    EDU_KEYS = [
        "id", "start_date", "end_date", "end_until_now", "college_name",
        "major_name", "degree", "description", "logo"
    ]

    PROJECTEXP_KEYS = [
        "id", "start_date", "end_date", "end_until_now", "name",
        "company_name", "description"
    ]

    AWARDS_KEYS = [
        "id", "reward_date", "name"
    ]

    WORKS_KEYS = [
        "id", "cover", "url", "description"
    ]

    INTENTION_KEYS = [
        "id", "city_name", "worktype", "position", "salary_code", "workstate", "industry"
    ]

    EMAIL_BASICINFO = ObjectDict({
        "birth": "出生年月",
        "nationality": "国籍",
        "gender_name": "性别",
        "city_name": "现居地",
        "weixin": "微信号",
        "qq": "QQ号",
        "email": "邮箱",
        "industry_name": "所属行业",
        "company_name": "当前公司",
        "current_job": "当前职位",
        "position_name": "职位职能",
    })

    EMAIL_INTENTION = ObjectDict({
        "positions": "职位",
        "salary_code_name": "薪资",
        "cities": "期望城市",
        "worktype_name": "工作类型",
    })

    @gen.coroutine
    def has_profile(self, user_id, locale=None, locale_display=None):
        """
        判断 user_user 是否有 profile (profile_profile 表数据)
        :param user_id:
        :return: tuple (bool, profile or None)

        调用方式:
        profile = has_profile[1]
        """

        result, profile = yield self.infra_profile_ds.get_profile(user_id)
        if locale:
            profile = self.__translate_profile(profile, locale, locale_display)
        return result, profile

    def __translate_profile(self, profile, locale=None, locale_display=None):
        others = profile.others
        if others and others[0]:
            other = others[0].get("other")
            if other:
                other = json_decode(other)
                for k, v in other.items():
                    if isinstance(v, str):
                        other[k] = locale.translate(v)
                    if k in ['residence', 'AddressProvince', 'CollegeCity']:
                        other[k] = (CITY.get(v) if locale_display == "en_US" else CITY_REVERSE.get(v)) or v
                    elif k in ['current_industry']:
                        other[k] = (INDUSTRY.get(v) if locale_display == "en_US" else INDUSTRY_REVERSE.get(v)) or v
                others[0]['other'] = json_encode(other)
        intentions = profile.intentions
        if intentions and intentions[0]:
            for k, v in intentions[0].items():
                if isinstance(v, str):
                    intentions[0][k] = locale.translate(v)
                else:
                    if k == 'cities' and v:
                        for city in v:
                            city['city_name'] = (CITY.get(city.get('city_name')) if locale_display == "en_US" else CITY_REVERSE.get(city.get('city_name'))) or city.get('city_name')
                    if k == 'industries':
                        for industry in v:
                            industry['industry_name'] = (INDUSTRY.get(industry.get('industry_name')) if locale_display == "en_US" else INDUSTRY_REVERSE.get(industry.get('industry_name'))) or industry.get('industry_name')
        self.logger.debug("translate_profile:{}".format(profile))
        return profile

    @gen.coroutine
    def has_profile_basic(self, profile_id):
        """判断 profile_id 是否有 profile_basic 数据
        因为 has_profile 接口中的 basic 数据存在并不能确定 profile_basic 表中，
        对应该 profile_id 的数据一定存在
        """

        result, data = yield self.get_profile_basic(profile_id)
        return bool(result) or not (data.status == infra_const.InfraStatusCode.not_exist)

    @gen.coroutine
    def has_profile_by_uuid(self, uuid):
        """
        判断 user_user 是否有 profile (profile_profile 表数据)
        :param uuid:
        :return: tuple (bool, profile or None)

        调用方式:
        profile = has_profile[1]
        """

        result, profile = yield self.infra_profile_ds.get_profile_by_uuid(uuid)
        return result, profile

    @gen.coroutine
    def has_profile_lite(self, user_id):
        """只返回 user_id 是否有 profile,
        has_profile 的简化版"""

        result = yield self.infra_profile_ds.has_profile(user_id)
        return result

    @gen.coroutine
    def import_profile(self, type_source, username, password, user_id, ua, company_id=None, token=None, appid=None,
                       unionid=None, version=None, captcha=None):
        """
        导入第三方简历（51job, 智联招聘，linkedin，猎聘）
        :param type_source: int 来源, 0:无法识别 1:51Job 2:Liepin 3:zhilian 4:linkedin
        :param username: string
        :param password: string
        :param user_id: int
        :param ua: int UA来源, 0:无法识别 1:微信端 2:移动浏览器 3:PC端
        :param token: string linkedin 网站的access_token
        :param company_id:
        :param captcha
        :return: tuple (bool, result or None)

        调用方式:
        profile = import_profile[1,"ab","123",2]
        """

        is_ok, result = yield self.infra_profile_ds.import_profile(
            int(type_source), username, password, user_id, company_id, int(ua), token, appid=appid, unionid=unionid,
            version=version, captcha=captcha)
        return is_ok, result

    @gen.coroutine
    def get_linkedin_token(self, code, redirect_url):
        """
        获得 linkedin oauth2.0的 access_token
        :param params: int
        :return:dict
        """

        params = ObjectDict(
            grant_type="authorization_code",
            code=code,
            redirect_uri=redirect_url,
            client_id=self.settings.linkedin_client_id,
            client_secret=self.settings.linkedin_client_secret,
        )

        response = yield self.infra_profile_ds.get_linkedin_token(params)
        return response

    @gen.coroutine
    def resume_upload(self, file_name, file_data, user_id):
        """手机上传简历
        """
        res = yield self.infra_profile_ds.resume_upload(file_name, file_data, user_id)
        return res

    @gen.coroutine
    def submit_upload_profile(self, name, mobile, user_id):
        """
        提交上传的简历
        :param name:
        :param mobile:
        :return:
        """
        params = ObjectDict({
            "name": name,
            "mobile": mobile
        })
        res = yield self.infra_profile_ds.infra_submit_upload_profile(params, user_id)
        return res

    @gen.coroutine
    def get_uploaded_profile(self, employee_id):
        """
        chatbot点击告诉ta时回填推荐信息
        :param employee_id:
        :return:
        """
        return (yield self.infra_profile_ds.get_uploaded_profile(employee_id))

    @gen.coroutine
    def submit_upload_profile_from_chatbot(self, name, mobile, employee_id, referral_reasons, file_name,
                                           relationship, recom_reason_text):
        """
        在chatbot简历上传页面提交推荐信息
        :param name:
        :param mobile:
        :param employee_id:
        :param referral_reasons:
        :param file_name:
        :param relationship:
        :param recom_reason_text:
        :return:
        """
        params = ObjectDict({
            'appid': const.APPID[env],
            'name': name,
            'mobile': mobile,
            'referral_reasons': referral_reasons,
            'file_name': file_name,
            'referral_type': 1,
            'relationship': relationship,
            'recom_reason_text': recom_reason_text
        })
        return (yield self.infra_profile_ds.infra_submit_upload_profile_from_chatbot(params, employee_id))

    @gen.coroutine
    def create_profile(self, user_id, source=const.PROFILE_SOURCE_PLATFORM):
        """ 创建 profile_profile 基础数据 """
        result, data = yield self.infra_profile_ds.create_profile(
            user_id, source)
        return result, data

    @gen.coroutine
    def get_profile_basic(self, profile_id):
        result, data = yield self.infra_profile_ds.get_profile_basic(
            profile_id)
        return result, data

    @gen.coroutine
    def create_profile_basic(self, params, profile_id, mode='m'):
        """
        创建 profile basic
        :param params:
        :param profile_id:
        :param mode: 'm': 手动（老6步）创建
        :return:
        """
        if mode == 'm':
            result, data = yield self.infra_profile_ds.create_profile_basic_manually(
                params, profile_id)
        elif mode == 'c':
            result, data = yield self.infra_profile_ds.create_profile_basic_custom(
                params, profile_id)
        else:
            raise ValueError('invalid mode')

        return result, data

    @gen.coroutine
    def update_profile_basic(self, profile_id, params):
        result, data = yield self.infra_profile_ds.update_profile_basic(
            profile_id, params)
        return result, data

    @gen.coroutine
    def get_profile_language(self, profile_id):
        result, data = yield self.infra_profile_ds.get_profile_language(
            profile_id)
        return result, data

    @gen.coroutine
    def create_profile_language(self, record, profile_id):
        result, data = yield self.infra_profile_ds.create_profile_language(
            record, profile_id)
        return result, data

    @gen.coroutine
    def update_profile_language(self, record, profile_id):
        result, data = yield self.infra_profile_ds.update_profile_language(
            record, profile_id)
        return result, data

    @gen.coroutine
    def delete_profile_language(self, record, profile_id):
        result, data = yield self.infra_profile_ds.delete_profile_language(
            record, profile_id)
        return result, data

    @gen.coroutine
    def get_profile_skill(self, profile_id):
        result, data = yield self.infra_profile_ds.get_profile_skill(
            profile_id)
        return result, data

    @gen.coroutine
    def create_profile_skill(self, record, profile_id):
        result, data = yield self.infra_profile_ds.create_profile_skill(
            record, profile_id)
        return result, data

    @gen.coroutine
    def update_profile_skill(self, record, profile_id):
        result, data = yield self.infra_profile_ds.update_profile_skill(
            record, profile_id)
        return result, data

    @gen.coroutine
    def delete_profile_skill(self, record, profile_id):
        result, data = yield self.infra_profile_ds.delete_profile_skill(
            record, profile_id)
        return result, data

    @gen.coroutine
    def get_profile_cert(self, profile_id):
        result, data = yield self.infra_profile_ds.get_profile_cert(
            profile_id)
        return result, data

    @gen.coroutine
    def create_profile_cert(self, record, profile_id):
        result, data = yield self.infra_profile_ds.create_profile_cert(
            record, profile_id)
        return result, data

    @gen.coroutine
    def update_profile_cert(self, record, profile_id):
        result, data = yield self.infra_profile_ds.update_profile_cert(
            record, profile_id)
        return result, data

    @gen.coroutine
    def delete_profile_cert(self, record, profile_id):
        result, data = yield self.infra_profile_ds.delete_profile_cert(
            record, profile_id)
        return result, data

    @gen.coroutine
    def get_profile_workexp(self, workexp_id):
        result, data = yield self.infra_profile_ds.get_profile_workexp(
            workexp_id)
        return result, data

    @gen.coroutine
    def create_profile_workexp(self, record, profile_id, mode='m', *args, **kwargs):
        if mode == 'm':
            # 通过老 6 步 profile 创建添加
            record.company_name = record.company
            record.job = record.position
        elif mode == 'c':
            # 通过 自定义简历编辑添加
            pass
        elif mode == 'p':
            # 通过 profile 编辑添加
            pass
        else:
            raise ValueError('invalid mode')

        result, data = yield self.infra_profile_ds.create_profile_workexp(
            record, profile_id)
        return result, data

    @gen.coroutine
    def update_profile_workexp(self, record, profile_id, *args, **kwargs):
        result, data = yield self.infra_profile_ds.update_profile_workexp(
            record, profile_id)
        return result, data

    @gen.coroutine
    def delete_profile_workexp(self, record, profile_id, *args, **kwargs):
        result, data = yield self.infra_profile_ds.delete_profile_workexp(
            record, profile_id)
        return result, data

    @gen.coroutine
    def get_profile_education(self, education_id):
        result, data = yield self.infra_profile_ds.get_profile_education(
            education_id)
        return result, data

    @gen.coroutine
    def create_profile_education(self, record, profile_id):
        college_code = yield self.infra_dict_ds.get_college_code_by_name(
            record.college_name)

        result, data = yield self.infra_profile_ds.create_profile_education(
            record, profile_id, college_code)

        return result, data

    @gen.coroutine
    def update_profile_education(self, record, profile_id):
        college_code = yield self.infra_dict_ds.get_college_code_by_name(
            record.college_name)
        result, data = yield self.infra_profile_ds.update_profile_education(
            record, profile_id, college_code)
        return result, data

    @gen.coroutine
    def delete_profile_education(self, record, profile_id):
        result, data = yield self.infra_profile_ds.delete_profile_education(
            record, profile_id)
        return result, data

    @gen.coroutine
    def get_profile_projectexp(self, projectexp_id):
        result, data = yield self.infra_profile_ds.get_profile_projectexp(
            projectexp_id)
        return result, data

    @gen.coroutine
    def create_profile_projectexp(self, record, profile_id):
        result, data = yield self.infra_profile_ds.create_profile_projectexp(
            record, profile_id)
        return result, data

    @gen.coroutine
    def update_profile_projectexp(self, record, profile_id):
        result, data = yield self.infra_profile_ds.update_profile_projectexp(
            record, profile_id)
        return result, data

    @gen.coroutine
    def delete_profile_projectexp(self, record, profile_id):
        result, data = yield self.infra_profile_ds.delete_profile_projectexp(
            record, profile_id)
        return result, data

    @gen.coroutine
    def get_profile_awards(self, profile_id):
        result, data = yield self.infra_profile_ds(
            {"profile_id": profile_id}, method="get", section="awards")
        return result, data

    @gen.coroutine
    def create_profile_awards(self, record, profile_id):
        result, data = yield self.infra_profile_ds.create_profile_awards(
            record, profile_id)
        return result, data

    @gen.coroutine
    def update_profile_awards(self, record, profile_id):
        result, data = yield self.infra_profile_ds.update_profile_awards(
            record, profile_id)
        return result, data

    @gen.coroutine
    def delete_profile_awards(self, record, profile_id):
        result, data = yield self.infra_profile_ds.delete_profile_awards(
            record, profile_id)
        return result, data

    @gen.coroutine
    def get_profile_works(self, works_id):
        result, data = yield self.infra_profile_ds.get_profile_works(works_id)
        return result, data

    @gen.coroutine
    def create_profile_works(self, record, profile_id):
        result, data = yield self.infra_profile_ds.create_profile_works(
            record, profile_id)
        return result, data

    @gen.coroutine
    def update_profile_works(self, record, profile_id):
        result, data = yield self.infra_profile_ds.update_profile_works(
            record, profile_id)
        return result, data

    @gen.coroutine
    def get_profile_intention(self, intention_id):
        result, data = yield self.infra_profile_ds.get_profile_intention(
            intention_id)
        return result, data

    @gen.coroutine
    def create_profile_intention(self, record, profile_id):
        result, data = yield self.infra_profile_ds.create_profile_intention(
            record, profile_id)
        return result, data

    @gen.coroutine
    def update_profile_intention(self, record, profile_id):
        result, data = yield self.infra_profile_ds.update_profile_intention(
            record, profile_id)
        return result, data

    @gen.coroutine
    def custom_cv_update_profile_education(self, profile_id, custom_cv):
        educations = custom_cv.get("education", [])

        if not educations:
            return

        for e in educations:
            status = e.get('__status', None)
            college_name = e.get('education_college_name')
            college_code = yield self.infra_dict_ds.get_college_code_by_name(
                college_name)

            end_until_now = int(e.get('education_end_until_now', '0'))

            if status:
                params = ObjectDict(
                    eid=e.get('id'),
                    profile_id=profile_id,
                    start_date=e.get('education_start'),
                    end_until_now=end_until_now,
                    college_name=college_name,
                    college_code=college_code,
                    major_name=e.get('education_major_name'),
                    degree=int(e.get('education_degree_hidden', '0')),
                    description=e.get('education_description_hidden'),
                    country_id=e.get("country_id")
                )
                if not end_until_now:
                    params.update(end_date=e.get('education_end'))

                if status == 'o':
                    yield self.create_profile_education(params, profile_id)

                elif status == 'x':
                    yield self.delete_profile_education(
                        {"id": params.eid}, profile_id=None)

                elif status == 'e':
                    params['id'] = params.eid
                    yield self.update_profile_education(params, profile_id)

    @gen.coroutine
    def custom_cv_update_profile_workexp(self, profile_id, custom_cv):
        workexps = custom_cv.get("workexp", [])

        if not workexps:
            return

        for w in workexps:
            status = w.get('__status', None)
            if status:
                end_until_now = int(w.get('workexp_end_until_now', '0'))

                params = ObjectDict(
                    wid=w.get('id'),
                    profile_id=profile_id,
                    start_date=w.get('workexp_start'),
                    end_until_now=end_until_now,
                    company_name=w.get('workexp_company_name'),
                    department_name=w.get('workexp_department_name'),
                    job=w.get('workexp_job'),
                    description=w.get('workexp_description_hidden')
                )
                if not end_until_now:
                    params.update(end_date=w.get('workexp_end'))

                if status == 'o':
                    yield self.create_profile_workexp(
                        params, profile_id, mode='c')

                elif status == 'x':
                    yield self.delete_profile_workexp(
                        {"id": params.wid}, profile_id=None)

                elif status == 'e':
                    params['id'] = params.wid
                    yield self.update_profile_workexp(params, profile_id)

    @gen.coroutine
    def custom_cv_update_profile_projectexp(self, profile_id, custom_cv):
        projectexps = custom_cv.get("projectexp", [])

        if not projectexps:
            return

        for p in projectexps:

            status = p.get('__status', None)
            if status:
                end_until_now = int(p.get('projectexp_end_until_now', '0'))

                params = ObjectDict(
                    id=p.get('id'),
                    profile_id=profile_id,
                    start_date=p.get('projectexp_start'),
                    end_until_now=end_until_now,
                    name=p.get('projectexp_name'),
                    role=p.get('projectexp_role'),
                    company_name=p.get('projectexp_company_name'),
                    description=p.get('projectexp_description_hidden'),
                    # responsibility=p.get("projectexp_responsibility")
                )
                if not end_until_now:
                    params.update(end_date=p.get('projectexp_end'))

                if status == 'o':
                    yield self.create_profile_projectexp(params, profile_id)

                elif status == 'x':
                    yield self.delete_profile_projectexp(
                        {"id": params.id}, profile_id=None)

                elif status == 'e':
                    yield self.update_profile_projectexp(params, profile_id)

    @gen.coroutine
    def custom_cv_update_profile_language(self, profile_id, custom_cv):
        languages = custom_cv.get("language", [])

        if not languages:
            return

        for p in languages:
            status = p.get('__status', None)
            if status:
                params = ObjectDict(
                    pid=p.get('id'),
                    profile_id=profile_id,
                    language=p.get('language_name'),
                    level=p.get('language_level')
                )
                if status == 'o':
                    yield self.create_profile_language(params, profile_id)

                elif status == 'x':
                    yield self.delete_profile_language(
                        {"id": params.pid}, profile_id=None)

                elif status == 'e':
                    params['id'] = params.pid
                    yield self.update_profile_language(params, profile_id)

    @gen.coroutine
    def custom_cv_update_profile_awards(self, profile_id, custom_cv):
        awards = custom_cv.get("awards", [])

        if not awards:
            return

        for p in awards:
            status = p.get('__status', None)
            if status:
                params = ObjectDict(
                    pid=p.get('id'),
                    profile_id=profile_id,
                    name=p.get('awards_name'),
                    reward_date=p.get('awards_reward_date')
                )
                if status == 'o':
                    yield self.create_profile_awards(params, profile_id)

                elif status == 'x':
                    yield self.delete_profile_awards(
                        {"id": params.pid}, profile_id=None)

                elif status == 'e':
                    params['id'] = params.pid
                    yield self.update_profile_awards(params, profile_id)

    @gen.coroutine
    def custom_cv_update_profile_skills(self, profile_id, custom_cv):
        skills = custom_cv.get("skills", [])

        if not skills:
            return

        for s in skills:
            status = s.get('__status', None)
            if status:
                params = ObjectDict(
                    pid=s.get('id'),
                    profile_id=profile_id,
                    name=s.get('skills_name')
                )
            if status == 'o':
                yield self.create_profile_skill(params, profile_id)

            elif status == 'x':
                yield self.delete_profile_skill(
                    {"id": params.pid}, profile_id=None)

            elif status == 'e':
                params['id'] = params.pid
                yield self.update_profile_skill(params, profile_id)

    @gen.coroutine
    def custom_cv_update_profile_credentials(self, profile_id, custom_cv):
        credentials = custom_cv.get("credentials", [])

        if not credentials:
            return

        for c in credentials:
            status = c.get('__status', None)
            if status:
                params = ObjectDict(
                    pid=c.get('id'),
                    profile_id=profile_id,
                    name=c.get('credentials_name')
                )
            if status == 'o':
                yield self.create_profile_cert(params, profile_id)

            elif status == 'x':
                yield self.delete_profile_cert(
                    {"id": params.pid}, profile_id=None)

            elif status == 'e':
                params['id'] = params.pid
                yield self.update_profile_cert(params, profile_id)

    @gen.coroutine
    def custom_cv_update_profile_intention(self, profile, custom_cv):
        profile_id = profile['profile']['id']
        position = custom_cv.get('position')
        expectedlocation = custom_cv.get('expectedlocation')
        salary_code = custom_cv.get("salary_code")
        worktype = custom_cv.get("worktype")
        workstate = custom_cv.get("workstate")
        industry = custom_cv.get("industry")

        has_intention = bool(profile.get("intentions"))

        record = ObjectDict()
        if expectedlocation:
            record.city_name = expectedlocation
        if position:
            record.position_name = position
        if salary_code:
            record.salary_code = salary_code
        if worktype:
            record.worktype = worktype
        if workstate:
            record.workstate = workstate
        if industry:
            record.industry = industry

        if has_intention:
            intention_id = first(profile.get("intentions")).get('id')

            record.id = intention_id
            yield self.update_profile_intention(
                record=record,
                profile_id=profile_id)
        else:
            yield self.create_profile_intention(
                record=record,
                profile_id=profile_id)

    @gen.coroutine
    def custom_cv_update_profile_works(self, profile, custom_cv):
        profile_id = profile['profile']['id']

        works = custom_cv.get('works')

        if works:
            record = ObjectDict()
            record.cover = first(works).get('works_cover')
            record.description = first(works).get('works_description')
            record.url = first(works).get('works_url')

            has_works = bool(profile.get("works"))
            if has_works:
                current_work = ObjectDict(first(profile.get("works")))
                record.id = current_work.id
                yield self.update_profile_works(
                    record=record, profile_id=profile_id)

            else:
                yield self.create_profile_works(
                    record=record, profile_id=profile_id)

    @gen.coroutine
    def update_profile_embedded_info_from_cv(self, profile_id, profile, custom_cv):
        """使用 custom_cv 更新 profile 的复合字段
            (education, workexp, projectexp, intention, works )
        :param profile_id: profile_id
        :param profile: profile
        :param custom_cv: 自定义简历模版输出 (dict)
        """

        # 多条复合字段
        yield self.custom_cv_update_profile_education(profile_id, custom_cv)

        yield self.custom_cv_update_profile_workexp(profile_id, custom_cv)

        yield self.custom_cv_update_profile_projectexp(profile_id, custom_cv)

        yield self.custom_cv_update_profile_language(profile_id, custom_cv)

        yield self.custom_cv_update_profile_awards(profile_id, custom_cv)

        yield self.custom_cv_update_profile_skills(profile_id, custom_cv)

        yield self.custom_cv_update_profile_credentials(profile_id, custom_cv)

        # 单条复合字段
        yield self.custom_cv_update_profile_intention(profile, custom_cv)

        yield self.custom_cv_update_profile_works(profile, custom_cv)

    @staticmethod
    def get_zodiac(date_string):
        """
        生日字符串 => 星座字符串
        :param date_string:
        :return:
        """
        try:
            date = datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            return ""

        month = date.month
        day = date.day

        if (month == 1 and day <= 20) or (month == 12 and day >= 22):
            return "mojie"
        elif (month == 1 and day >= 21) or (month == 2 and day <= 18):
            return "shuiping"
        elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
            return "shuangyu"
        elif (month == 3 and day >= 21) or (month == 4 and day <= 20):
            return "baiyang"
        elif (month == 4 and day >= 21) or (month == 5 and day <= 20):
            return "jinniu"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 21):
            return "shuangzi"
        elif (month == 6 and day >= 22) or (month == 7 and day <= 22):
            return "juxie"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 23):
            return "shizi"
        elif (month == 8 and day >= 24) or (month == 9 and day <= 23):
            return "chunv"
        elif (month == 9 and day >= 24) or (month == 10 and day <= 23):
            return "tiancheng"
        elif (month == 10 and day >= 24) or (month == 11 and day <= 22):
            return "tianxie"
        elif (month == 11 and day >= 23) or (month == 12 and day <= 21):
            return "sheshou"

    @gen.coroutine
    def get_custom_tpl_all(self):
        """自定义简历模板原表数据获取"""
        ret = yield self.config_sys_cv_tpl_ds.get_config_sys_cv_tpls(
            conds={'disable': const.OLD_YES},
            fields=['field_name', 'field_title', 'map', 'validate_re']
        )
        return ret

    @gen.coroutine
    def profile_to_tempalte(self, p_profile, locale=None):
        """ 将从基础服务获得的 profile dict 转换成模版格式
        :param p_profile: 从基础服务获得的 profile dict
        :param locale: 国际化
        """
        assert isinstance(p_profile, dict)

        p_profile = ObjectDict(p_profile)

        p_basic = ObjectDict(p_profile.get("basic"))
        p_workexp = p_profile.get("workexps")
        p_education = p_profile.get("educations")
        p_projectexps = p_profile.get("projectexps")
        p_languages = p_profile.get("languages")
        p_skills = p_profile.get("skills")
        p_certificates = p_profile.get("credentials")
        p_awards = p_profile.get("awards")
        p_works = p_profile.get("works")
        p_intentions = p_profile.get('intentions')
        p_attachments = p_profile.get('attachments')
        p_others = p_profile.get('others')

        profile = ObjectDict()
        profile.gender = ""
        if p_basic.get("gender") == 1:
            profile.gender = "male"
        elif p_basic.get("gender") == 2:
            profile.gender = "female"

        profile.avatar_url = p_basic.get("headimg", "")
        profile.username = p_basic.get("name", "")
        profile.description = p_basic.get("motto", "")
        profile.job = p_basic.get("current_job", "")
        profile.company = p_basic.get("company_name", "")
        profile.location = p_basic.get("city_name", "")
        profile.zodiac = self.get_zodiac(p_basic.get("birth", ""))
        profile.introduction = p_basic.get("self_introduction", "")

        # experiences
        experiences = list()
        for w in p_workexp:
            experience_item = ObjectDict()
            experience_item.id = w.get("id")
            experience_item.job = w.get("job", "")
            experience_item.dep = w.get("department_name", "")
            experience_item.company = w.get("company_name", "")
            experience_item.logo = w.get("company_logo", "")
            start_date = w.get("start_date", "")
            end_date = w.get("end_date", "")
            if not end_date or int(w.get("end_until_now", 0)):
                experience_item.time = start_date[:7] + " " + locale.translate(const.UNTIL_NOW) if locale else "至今"
            else:
                experience_item.time = start_date[:7] + " " + (locale.translate(const.TO) if locale else "至") + " " + end_date[:7]
            experience_item.description = w.get("description", "")
            experiences.append(experience_item)
        profile.experiences = experiences

        # education
        degree_list = yield self.infra_dict_ds.get_const_dict(parent_code=const.CONSTANT_PARENT_CODE.DEGREE_USER)
        educations = list()
        for e in p_education:
            education_item = ObjectDict()
            education_item.id = e.get("id")
            education_item.job = e.get("major_name", "")
            education_item.dep = locale.translate(degree_list.get(str(e.get("degree", 0)), "无"))

            education_item.company = e.get("college_name", "")
            education_item.logo = e.get("college_logo", "")
            start_date = e.get("start_date", "")
            end_date = e.get("end_date", "")
            if not end_date or int(e.get("end_until_now", 0)):
                education_item.time = start_date[:7] + " " + locale.translate(const.UNTIL_NOW) if locale else "至今"
            else:
                education_item.time = start_date[:7] + " " + (locale.translate(const.TO) if locale else "至") + " " + end_date[:7]

            education_item.description = e.get("description", "")
            educations.append(education_item)
        profile.educations = educations

        # projects
        projects = list()
        for p in p_projectexps:
            project_item = ObjectDict()
            project_item.id = p.get("id")
            project_item.job = p.get("name", "")
            project_item.company = p.get("company_name", "")
            project_item.description = p.get("description", "")
            start_date = p.get("start_date", "")
            end_date = p.get("end_date", "")
            if not end_date or int(p.get("end_until_now", 0)):
                project_item.time = start_date[:7] + " " + locale.translate(const.UNTIL_NOW) if locale else "至今"
            else:
                project_item.time = start_date[:7] + " " + (locale.translate(const.TO) if locale else "至") + " " + end_date[:7]
            projects.append(project_item)
        profile.projects = projects

        # language
        languages = list()
        for l in p_languages:
            language_item = ObjectDict()
            language_item.volume = l.get("level", "")
            language_item.label = l.get("name", "")
            languages.append(language_item)
        profile.languages = languages

        # technical
        abilities = []
        for s in p_skills:
            abilities.append(s.get("name", ""))
        profile.abilities = abilities

        # certicate
        certificate = []
        for c in p_certificates:
            certificate.append(c.get("name", ""))
        profile.certificate = certificate

        # prize
        prizes = []
        for a in p_awards:
            prize_item = ObjectDict()
            prize_item.id = a.get("id")
            prize_item.time = a.get("reward_date", "")[:7]
            prize_item.text = (
                a.get("name", "") + a.get("award_winning_status", ""))
            prizes.append(prize_item)
        profile.prizes = prizes

        # links
        link = {}
        if p_works:
            l = p_works[0]
            link = ObjectDict()
            link.id = l.get("id")
            link.link = l.get("url")
            link.text = l.get("name")
            link.description = l.get("description")
            link.cover = l.get("cover", "")

        profile.link = link

        # intention
        job_apply = {}
        if p_intentions:
            intention = p_intentions[0]
            position = ""
            if intention.get("positions", []):
                for p in intention.get("positions"):
                    position = position + p.get("position_name") + ","
                position = position[0: len(position) - 1]

            worktype_name = intention.get("worktype_name", "未选择")

            location = ""
            if intention.get("cities", []):
                for city in intention.get("cities"):
                    location = location + city.get("city_name") + ","
                location = location[0: len(location) - 1]
            salary = intention.get('salary_code_name', "")

            workstate = intention.get("workstate_name")

            industry = ""
            if intention.get("industries", []):
                for i in intention.get("industries"):
                    industry = industry + i.get("industry_name") + ","
                industry = industry[0: len(industry) - 1]

            job_apply.update({
                "id": intention.get("id"),
                "position": position,
                "type": worktype_name,
                "location": location,
                "salary": salary,
                "workstate": workstate,
                "industry": industry
            })
        profile.job_apply = job_apply

        # attachment
        if p_attachments:
            attachment = {}
            p_attachment = p_attachments[0]
            attachment.update(
                create_time=p_attachment.get('create_time')[:-3],
                path=p_attachment.get('path'),
                name=p_attachment.get('name'))
            profile.attachment = attachment

        if p_others:
            # 为某些自定义字段添加单位
            if first(p_others).get('other'):
                other = ObjectDict(json_decode(first(p_others).get('other')))

                if other.workyears:
                    other.workyears = other.workyears + locale.translate('年')

                profile.other = other

        return profile

    @staticmethod
    def has_current_job(profile):
        """ 判断 profile 是否包含"含有至今"的工作信息 """
        wexps = profile.get('workexps', [])
        if wexps:
            return len(list(filter(
                lambda w: w.get("end_until_now", 0) == 1, wexps))) > 0
        return False

    @staticmethod
    def get_current_job(profile):
        """ 获取 profile 中最新的一条"含有至今"的工作信息 """
        wexps = profile.get('workexps', [])

        latest_jobs = list(
            filter(lambda w: w.get("end_until_now", 0) == 1, wexps))
        return (sorted(latest_jobs, key=lambda x: x.get("start_date", ""),
                       reverse=True)[0])

    @staticmethod
    def get_latest_job(profile):
        """ 获取最新的一条工作记录 """
        wexps = profile.get('workexps', [])
        return (sorted(wexps, key=lambda x: x.get('start_date', ""),
                       reverse=True)[0])

    @gen.coroutine
    def get_others_key_name_mapping(self, company_id=0, select_all=False, locale=None):
        """获取自定义字段 name 和 title 的键值对，供前端在展示 profile 的时候使用"""
        metadatas = yield self.infra_profile_ds.get_custom_metadata(company_id, select_all)

        rename_mapping = {
            'fieldName': 'field_name',
            'fieldTitle': 'field_title',
            'fieldType': 'field_type'
        }

        def _gen(metadatas):
            for m in metadatas:
                if not m.get('map'):
                    if locale:
                        m['fieldTitle'] = locale.translate(m.get('fieldTitle'))
                    target = sub_dict(m, ['fieldName', 'fieldTitle', 'fieldType'])
                    yield rename_keys(target, rename_mapping)

        return list(_gen(metadatas))

    @staticmethod
    def convert_customcv(custom_cv, custom_cv_tpls, target=None):
        if not target:
            raise TypeError('target cannot be None')

        if not re.match(r'^other|user_user|(profile_[a-z]+)$', target):
            # possible values:
            # user_user
            # profile_basic
            # profile_education
            # profile_workexp
            # profile_projectexp
            # profile_awards
            # profile_works
            # other
            raise ValueError('incorrect target value')

        key_mapping = None
        if target is not 'other':
            target_keys = [c.field_name for c in custom_cv_tpls
                           if c.map and c.map.startswith(target)]

            key_mapping = {c.field_name: c.map.split('.')[1] for c in custom_cv_tpls
                           if c.map and c.map.startswith(target)}

        else:
            target_keys = [c.field_name for c in custom_cv_tpls
                           if not c.map]

        target = sub_dict(custom_cv, target_keys)

        if key_mapping:
            target = rename_keys(target, key_mapping)

        return {k: v for k, v in target.items() if v is not None}

    @gen.coroutine
    def is_resume_upload_complete(self, user_id, sync_id, employee_id):
        """轮训Java后端简历上传是否完成"""
        params = {
            "userId": user_id,
            "syncId": sync_id,
            "employeeId": employee_id
        }
        res = yield self.infra_profile_ds.infra_is_resume_upload_complete(params)
        return res

    @gen.coroutine
    def referral_upload_resume_info(self, user_id, sync_id, employee_id):
        """小助手上传的简历信息"""
        params = {
            "userId": user_id,
            "syncId": sync_id,
            "employeeId": employee_id
        }
        res = yield self.infra_profile_ds.infra_referral_upload_resume_info(params)
        return res

    @gen.coroutine
    def import_apply_profile(self):
        """仟寻简历导入页面"""

        # 跳转模版需要的参数初始值
        # redirect_params = {
        #     "use_email": False,
        #     "goto_custom_url": '',
        # }
        # 获取最佳东方导入开关
        need_profile_upload = [570004]  # 现在为沙盒的
        company = yield CompanyPageService().get_company({'id': self.current_user.wechat.company_id}, need_conf=True)
        importer = ObjectDict(profile_import_51job=self.make_url(path.RESUME_URL, self.params, m='authorization',
                                                                 way=const.RESUME_WAY_51JOB),
                              profile_import_zhilian=self.make_url(path.RESUME_URL, self.params, m='authorization',
                                                                   way=const.RESUME_WAY_ZHILIAN),
                              # profile_import_zhilian=None,
                              # set later.
                              profile_import_liepin=None,
                              profile_import_linkedin=self.make_url(path.RESUME_URL, self.params, m='authorization',
                                                                    way=const.RESUME_WAY_LINKEDIN),
                              # profile_import_linkedin=None,
                              # set later.
                              profile_import_maimai=None,
                              # set later
                              profile_import_veryeast=None,
                              # set later
                              profile_resume_upload=None,
                              # set later
                              profile_email=None,
                              profile_create_30s=self.make_url(path.PROFILE_NEW, self.params, m='authorization',
                                                               way=const.RESUME_WAY_30S),
                              profile_import_pc=True,
                              # set later
                              profile_custom_url=None)
        if company.conf_veryeast_switch == 1:
            importer.update(profile_import_veryeast=self.make_url(path.RESUME_URL, self.params, m='authorization',
                                                                  way=const.RESUME_WAY_VERYEAST))
        if company.id in need_profile_upload:
            importer.update(profile_resume_upload=self.make_url(path.RESUME_UPLOAD, self.params))

        # 如果是申请中跳转到这个页面，需要做详细检查
        current_path = self.request.uri.split('?')[0]
        paths_for_application = [path.APPLICATION, path.PROFILE_PREVIEW]
        paths_for_import = [path.IMPORT_PROFILE]

        self.logger.warn(current_path)
        self.logger.warn(self.params)

        profile_email_url = self.make_url('/application/email', self.params, way=const.RESUME_WAY_MOSEEKER)

        if (current_path in paths_for_application and
            self.params.pid and self.params.pid.isdigit()):

            pid = int(self.params.pid)
            position = yield PositionPageService().get_position(pid, display_locale=self.get_current_locale())

            self.logger.warn(position)

            # 判断是否可以接受 email 投递
            if position.email_resume_conf == const.OLD_YES:
                importer.update(
                    profile_email=profile_email_url
                )
            # redirect_params.update(
            #     use_email=(position.email_resume_conf == const.OLD_YES))

            # 自定义职位
            if position.app_cv_config_id:
                goto_custom_url = self.make_url(
                    path.PROFILE_CUSTOM_CV,
                    self.params)
                # update
                self.redirect(goto_custom_url)
                return

                # 如果是自定义职位，且没有 profile，且是直接投递定制的公司
                # 直接跳转到自定义填写页面

                # is_direct_apply = yield self.customize_ps.create_direct_apply(
                #     position.company_id, position.app_cv_config_id)
                #
                # if is_direct_apply:
                #     self.redirect(goto_custom_url)
                #     return
                # else:
                #     importer.update(
                #         profile_custom_url= goto_custom_url
                #     )
                # redirect_params.update(goto_custom_url=goto_custom_url)
        elif current_path in paths_for_import:
            importer.update(
                profile_create_30s=None,
                profile_import_pc=None
            )

            pid = int(self.params.pid)
            position = yield PositionPageService().get_position(pid, display_locale=self.get_current_locale())

            self.logger.warn(position)

            # 判断是否可以接受 email 投递
            if position.email_resume_conf == const.OLD_YES:
                importer.update(
                    profile_email=profile_email_url
                )

            # 自定义职位
            goto_custom_url = self.make_url(
                path.PROFILE_CUSTOM_CV,
                self.params)
            importer.update(
                profile_custom_url=goto_custom_url
            )

        else:
            # 从侧边栏直接进入，允许使用 email 创建 profile
            # redirect_params.update(use_email=True)
            importer.update(
                profile_email=profile_email_url
            )

        # ========== MAIMAI OAUTH ===============
        # 拼装脉脉 oauth 路由
        cusdata = "?recom={}&pid={}&wechat_signature={}".format(self.params.recom, self.params.pid,
                                                                self.current_user.wechat.signature)
        # 加上渠道
        cusdata = "{}&way={}".format(cusdata, const.FROM_MAIMAI)
        # 脉脉cusdata中不允许出现 '&' ，考虑我们公司目前的使用的参数中不会出现 '$$' , 将 '&' 转为 '$$' 使用
        cusdata = cusdata.replace("&", "$$")
        self.logger.info("[maimai_url_cusdata: {}]".format(cusdata))

        cusdata = urlencode(dict(cusdata=cusdata))
        appid = self.settings.maimai_appid
        maimai_url = path.MAIMAI_ACCESSTOKEN.format(appid=appid, cusdata=cusdata)

        # 猎聘用户授权 现场数据缓存
        lielin_dict = dict(pid=self.params.pid,
                           wechat_signature=self.current_user.wechat.signature)
        if self.params.recom:
            lielin_dict.update(recom=self.params.recom)

        base_cache = BaseRedis()
        base_cache.set(
            const.LIEPIN_SCENE_KEY_FMT.format(
                sysuser_id=self.current_user.sysuser.id
            ),
            json.dumps(lielin_dict),
            const.LIEPIN_SCENE_KEY_TTL
        )

        # 第三方简历导入对接回调地址配置
        importer.update(
            profile_import_liepin=path.LIEPIN_ACCESSTOKEN.format(
                hashlib.sha1(str(self.current_user.sysuser.id).encode('u8')).hexdigest()
            ),
            profile_import_maimai=maimai_url
        )

        # 是否需要弹出 隐私协议 窗口
        user_id = self.current_user.sysuser.id
        result, data = yield PrivacyPageService().if_privacy_agreement_window(user_id)
        # redirect_params.update(
        #     # show_privacy_agreement=data,
        #     wechat_signature=self.current_user.wechat.signature
        # )

        # redirect_params = {**self.params, **redirect_params}

        self.render_page(
            template_name='profile/importresume.html',
            data=dict(
                show_privacy_agreement=data,
                importer=importer
            )
        )
