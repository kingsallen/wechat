# coding=utf-8

import re
from datetime import datetime

import tornado.gen as gen
from tornado.escape import json_decode

import conf.common as const
from service.page.base import PageService
from util.common import ObjectDict
from util.tool.date_tool import curr_datetime_now
from util.tool.dict_tool import purify


class ProfilePageService(PageService):
    """对接profile服务
    referer: https://wiki.moseeker.com/profile-api.md
    """

    FE_ROUTES = ObjectDict({
        "basic":          "basic",
        "description":    "basic",
        "jobexp":         "workexp",
        "projectexp":     "projectexp",
        "jobpref":        "intention",
        "language":       "language",
        "skill":          "skill",
        "cert":           "credentials",
        "link":           "works",
        "prize":          "awards",
        "eduexp":         "education",
        "jobexp_company": "jobexp_company"
    })

    BASIC_KEYS = [
        'name', 'birth', 'city_name', 'gender', 'motto', 'self_introduction',
        'profile_id'
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
        "id", "city_name", "worktype", "position_name", "salary_code"
    ]

    @gen.coroutine
    def has_profile(self, user_id):
        """
        判断 user_user 是否有 profile (profile_profile 表数据)
        :param user_id:
        :return: tuple (bool, profile or None)

        调用方式:
        profile = has_profile[1]
        """

        result, profile = yield self.infra_profile_ds.get_profile(user_id)
        return result, profile

    @gen.coroutine
    def import_profile(self, source, username, password, user_id, token=None):
        """
        导入第三方简历（51job, 智联招聘，linked，猎聘）
        :param source: int
        :param username: string
        :param password: string
        :param user_id: int
        :param token: string linkedin 网站的access_token
        :return: tuple (bool, result or None)

        调用方式:
        profile = import_profile[1,"ab","123",2]
        """

        is_ok, result = yield self.infra_profile_ds.import_profile(source,
                                                                   username,
                                                                   password,
                                                                   user_id,
                                                                   token)
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
    def create_profile_workexp(self, record, profile_id, mode='m'):
        if mode == 'm':
            # 经过前端的命名修改后这些都不需要了
            # record.company_name = record.company
            # record.job = record.position
            # record.start_date = record.start + '-01'
            # if record.end == '至今':
            #     record.end_until_now = 1
            # else:
            #     record.end_date = record.end + '-01'
            #     record.end_until_now = 0
            pass

        else:
            raise ValueError('invalid mode')

        result, data = yield self.infra_profile_ds.create_profile_workexp(
            record, profile_id)
        return result, data

    @gen.coroutine
    def update_profile_workexp(self, record, profile_id):
        result, data = yield self.infra_profile_ds.update_profile_workexp(
            record, profile_id)
        return result, data

    @gen.coroutine
    def delete_profile_workexp(self, record, profile_id):
        result, data = yield self.infra_profile_ds.delete_profile_workexp(
            record, profile_id)
        return result, data

    @gen.coroutine
    def get_profile_education(self, education_id):
        result, data = yield self.infra_profile_ds.get_profile_education(
            education_id)
        return result, data

    @gen.coroutine
    def create_profile_education(self, record, profile_id, mode='m'):
        if mode == 'm':  # 老六步
            # 经过前端的命名修改以后，这些都不需要了
            # record.college_name = record.university
            # record.degree = record.diploma
            # record.start_date = record.start + '-01'
            # if record.end == '至今':
            #     record.end_until_now = 1
            # else:
            #     record.end_date = record.end + '-01'
            #     record.end_until_now = 0
            pass

        else:
            raise ValueError('invalid mode')

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
    def update_profile_embedded_info_from_cv(self, profile_id, custom_cv):
        """使用 custom_cv 更新 profile 的复合字段 (education, workexp, projectext)
        :param profile_id: profile_id
        :param custom_cv: 自定义简历模版输出 (dict)
        """
        custom_cv = ObjectDict(custom_cv)
        education = custom_cv.get("education", [])
        workexp = custom_cv.get("workexp", [])
        projectexp = custom_cv.get("projectexp", [])

        for e in education:
            status = e.get('__status', None)
            college_name = e.get('school')
            college_code = yield self.infra_dict_ds.get_college_code_by_name(
                college_name)

            if status:
                params = ObjectDict(
                    eid=e.get('id'),
                    profile_id=profile_id,
                    start_date=e.get('start'),
                    end_date=e.get('end'),
                    end_until_now=1 if e.get('end') == u"至今" else 0,
                    college_name=college_name,
                    college_code=college_code,
                    major_name=e.get('major'),
                    degree=int(e.get('degree', '0'))
                )
                if status == 'o':
                    yield self.create_profile_education(params, profile_id)

                elif status == 'x':
                    yield self.delete_profile_education({"id": params.eid})

                elif status == 'e':
                    params['id'] = params.eid
                    yield self.update_profile_education(params)

        for w in workexp:
            status = w.get('__status', None)
            if status:
                params = ObjectDict(
                    wid=w.get('id'),
                    profile_id=profile_id,
                    start_date=w.get('start'),
                    end_date=w.get('end'),
                    end_until_now=1 if w.get('end') == u"至今" else 0,
                    company_name=w.get('company'),
                    department_name=w.get('department'),
                    job=w.get('position'),
                    description=w.get('describe')
                )
                if status == 'o':
                    yield self.create_profile_workexp(params, profile_id)

                elif status == 'x':
                    yield self.delete_profile_workexp({"id": params.wid})

                elif status == 'e':
                    params['id'] = params.wid
                    yield self.update_profile_workexp(params)

        for p in projectexp:
            status = p.get('__status', None)
            if status:
                params = ObjectDict(
                    pid=p.get('id'),
                    profile_id=profile_id,
                    start_date=p.get('start'),
                    end_date=p.get('end'),
                    end_until_now=1 if p.get('end') == u"至今" else 0,
                    name=p.get('name'),
                    role=p.get('position'),
                    description=p.get('introduce'),
                    responsibility=p.get("describe")
                )
                if status == 'o':
                    yield self.create_profile_projectexp(params, profile_id)

                elif status == 'x':
                    yield self.delete_profile_projectexp({"id": params.pid})

                elif status == 'e':
                    params['id'] = params.pid
                    yield self.update_profile_projectexp(params)

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
        ret = yield self.config_sys_cv_tpl_ds.get_config_sys_cv_tpls(
            conds={'disable': const.OLD_YES},
            fields=['field_name', 'field_title', 'map']
        )
        return ret

    @gen.coroutine
    def profile_to_tempalte(self, p_profile, other_json=None):
        """将从基础服务获得的 profile dict 转换成模版格式
        :param p_profile: 从基础服务获得的 profile dict
        :param other_json: "其它"数据
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
        profile.job = p_basic.get("position_name", "")
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
                experience_item.time = start_date[:7] + u" 至今"
            else:
                experience_item.time = start_date[:7] + u" 至 " + end_date[:7]
            experience_item.description = w.get("description", "")
            experiences.append(experience_item)
        profile.experiences = experiences

        # education
        degree_list = yield self.infra_dict_ds.get_const_dict(
            parent_code=const.CONSTANT_PARENT_CODE.DEGREE_USER)
        educations = list()
        for e in p_education:
            education_item = ObjectDict()
            education_item.id = e.get("id")
            education_item.job = e.get("major_name", "")
            education_item.dep = degree_list.get(str(e.get("degree", 0)), "无")

            education_item.company = e.get("college_name", "")
            education_item.logo = e.get("college_logo", "")
            start_date = e.get("start_date", "")
            end_date = e.get("end_date", "")
            if not end_date or int(e.get("end_until_now", 0)):
                education_item.time = start_date[:7] + u" 至今"
            else:
                education_item.time = start_date[:7] + u" 至 " + end_date[:7]

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
                project_item.time = start_date[:7] + u" 至今"
            else:
                project_item.time = start_date[:7] + u" 至 " + end_date[:7]
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
            position = u""
            if intention.get("positions", []):
                position = intention.get("positions")[0].get('position_name',
                                                             '')

            worktype_name = intention.get("worktype_name", u"未选择")

            location = u""
            if intention.get("cities", []):
                location = intention.get("cities")[0].get('city_name', '')

            salary = intention.get('salary_code_name', "")

            job_apply.update({
                "id":       intention.get("id"),
                "position": position,
                "type":     worktype_name,
                "location": location,
                "salary":   salary
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
            other_json = ObjectDict(json_decode(p_others[0].get('other')))
            sys_cv_tpls = yield self.get_custom_tpl_all()
            other = ObjectDict()
            other.keyvalues = []

            for k, v in other_json.items():
                if v:
                    if isinstance(v, list):
                        setattr(other, k, v)
                        continue
                    if k == "IDPhoto":
                        setattr(other, "id_photo", v)
                        continue
                    try:
                        lvm = {
                            "label": [e.field_title for e in sys_cv_tpls if e.field_name == k][0],
                            "value": v
                        }
                    except KeyError:
                        continue
                    other.keyvalues.append(lvm)
            profile.other = other

        return profile

    @staticmethod
    def calculate_workyears(p_workexps):
        """ 计算工作年份 """
        min_start_date = None
        max_end_date = None
        until_now = False
        workyears = 0
        try:
            for workexp in p_workexps:
                if (min_start_date is None or min_start_date > workexp.get(
                    "start_date")):
                    min_start_date = workexp.get("start_date")

                if (max_end_date is None or max_end_date < workexp.get(
                    "end_date")):
                    max_end_date = workexp.get("end_date")

                if not until_now and workexp.get(
                    "end_until_now"): until_now = workexp.get("end_until_now")

            if until_now:
                max_end_date = curr_datetime_now().year
            else:
                max_end_date = max_end_date[:4]
            workyears = (int(max_end_date) - int(min_start_date[:4]))
        except Exception:
            workyears = 0
        finally:
            return workyears

    def get_job_for_application(self, profile):
        """ 获取最新的工作经历用以申请 """
        if not profile.get("workexps", []):
            return ObjectDict()

        if self.has_current_job(profile):
            return self.get_current_job(profile)

        return self.get_latest_job(profile)

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
    def custom_fields_need_kvmapping(self, config_cv_tpls):
        """
        工具方法，
        查找 config_cv_tpls 表中值为字典值的数据，
        然后组合成如下数据结构：(截止至 2017-03-24)
        {
            'AddressProvince':       {
                'title': '地址所在省/直辖市',
                'value': {'0':  '',
                          '1':  '安徽省',
                          '10': '海南省',
                          '11': '河北省',
                          '12': '河南省',
                          '13': '黑龙江省',
                          '14': '湖北省',
                          '15': '湖南省',
                          '16': '吉林省',
                          '17': '江苏省',
                          '18': '江西省',
                          '19': '辽宁省',
                          '2':  '澳门',
                          '20': '内蒙古自治区',
                          '21': '宁夏回族自治区',
                          '22': '青海省',
                          '23': '山东省',
                          '24': '山西省',
                          '25': '陕西省',
                          '26': '上海',
                          '27': '四川省',
                          '28': '天津',
                          '29': '台湾省',
                          '3':  '北京',
                          '30': '香港',
                          '31': '西藏自治区',
                          '32': '新疆省',
                          '33': '浙江省',
                          '34': '云南省',
                          '4':  '重庆',
                          '5':  '福建省',
                          '6':  '甘肃省',
                          '7':  '广东省',
                          '8':  '广西省',
                          '9':  '贵州省'}},
            'ExpectedInterviewCity': {'title': '期望面试城市',
                                      'value': {'0': '',
                                                '1': '哈尔滨',
                                                '2': '沈阳',
                                                '3': '石家庄',
                                                '4': '重庆',
                                                '5': '青岛',
                                                '6': '济南',
                                                '7': '无锡',
                                                '8': '郑州',
                                                '9': '开封'}},
            'InterestedJobFunction': {'title': ' 感兴趣职能',
                                      'value': {'0':  '',
                                                '1':  '行政管理',
                                                '10': '市场营销',
                                                '11': '生产制造',
                                                '12': '采购',
                                                '13': '研发',
                                                '14': '销售',
                                                '15': '供应链计划/物流',
                                                '16': '宠物医院服务',
                                                '17': '动物医学',
                                                '18': '兽医师（未持证）',
                                                '19': '职业技术/技工',
                                                '2':  '企业事务/公共关系',
                                                '20': '培训生项目',
                                                '21': '实习生',
                                                '3':  '法律/合规',
                                                '4':  '执业兽医师',
                                                '5':  '工程/机械',
                                                '6':  '财务',
                                                '7':  '医疗护理',
                                                '8':  '人力资源',
                                                '9':  'IT信息技术'}},
            'InterestingExtent':     {'title': '感兴趣程度',
                                      'value': {'0': '',
                                                '1': '暂不考虑新的工作机会',
                                                '2': '随意浏览，了解工作机会',
                                                '3': '积极求职，目前处于在职状态',
                                                '4': '可以立即入职'}},
            'IsFreshGraduated':      {'title': '应届/往届',
                                      'value': {'0': '', '1': '应届',
                                                '2': '往届'}},
            'JapaneseLevel':         {'title': '日语等级',
                                      'value': {'0': '',
                                                '1': '一级',
                                                '2': '二级',
                                                '3': '三级',
                                                '4': '四级',
                                                '5': '未通过'}},
            'PoliticalStatus':       {'title': '政治面貌',
                                      'value': {'0': '',
                                                '1': '中共党员(含预备党员)',
                                                '2': '团员',
                                                '3': '群众'}},
            'cpa':                   {'title': 'CPA证书',
                                      'value': {'0': '', '1': '有CPA',
                                                '2': '无CPA'}},
            'degree':                {'title': '学历',
                                      'value': {'0': '',
                                                '1': '大专以下',
                                                '2': '大专',
                                                '3': '本科',
                                                '4': '硕士',
                                                '5': '博士',
                                                '6': '博士以上'}},
            'expectsalary':          {'title': '期望年薪',
                                      'value': {'0': '',
                                                '1': '6万以下',
                                                '2': '6万-8万',
                                                '3': '8万-12万',
                                                '4': '12-20万',
                                                '5': '20万-30万',
                                                '6': '30万以上'}},
            'frequency':             {'title': '选择班次',
                                      'value': {'0': '', '1': '早', '2': '中',
                                                '3': '晚'}},
            'gender':                {'title': '性别',
                                      'value': {'0': '', '1': '男', '2': '女'}},
            'icanstart':             {'title': '到岗时间',
                                      'value': {'0': '',
                                                '1': '随时',
                                                '2': '两周',
                                                '3': '一个月',
                                                '4': '一个月以上'}},
            'industry':              {'title': '期望行业',
                                      'value': {'0':  '',
                                                '1':  '计算机/通信/电子/互联网',
                                                '10': '服务业',
                                                '11': '文化/传媒/娱乐/体育',
                                                '12': '能源/矿产/环保',
                                                '13': '政府/非盈利机构/其他',
                                                '2':  '会计/金融/银行/保险',
                                                '3':  '房地产/建筑业',
                                                '4':  '商业服务/教育/培训',
                                                '5':  '贸易/批发/零售/租赁业',
                                                '6':  '制药/医疗',
                                                '7':  '广告/媒体',
                                                '8':  '生产/加工/制造',
                                                '9':  '交通/运输/物流/仓储'}},
            'majorrank':             {'title': '专业排名',
                                      'value': {'0': '',
                                                '1': '5%',
                                                '2': '5%—15%',
                                                '3': '15%-30%',
                                                '4': '30%-50%',
                                                '5': '50%以下'}},
            'marriage':              {'title': '婚姻状况',
                                      'value': {'0': '', '1': '未婚',
                                                '2': '已婚'}},
            'nightjob':              {'title': '是否接受夜班',
                                      'value': {'0': '', '1': '接受',
                                                '2': '不接受'}},
            'residencetype':         {'title': '户口类型',
                                      'value': {'0': '', '1': '农业户口',
                                                '2': '非农业户口'}},
            'salary':                {'title': '当前年薪',
                                      'value': {'0': '',
                                                '1': '6万以下',
                                                '2': '6万-8万',
                                                '3': '8万-12万',
                                                '4': '12-20万',
                                                '5': '20万-30万',
                                                '6': '30万以上'}},
            'servedoffice':          {'title': '曾供职事务所',
                                      'value': {'0': '',
                                                '1': 'KPMG',
                                                '2': 'Deloitte',
                                                '3': 'PWC',
                                                '4': 'EY',
                                                '5': '其他'}},
            'trip':                  {'title': '是否接受长期出差',
                                      'value': {'0': '', '1': '接受',
                                                '2': '不接受'}},
            'workdays':              {'title': '每周到岗天数(实习)',
                                      'value': {'0': '',
                                                '1': '1天/周',
                                                '2': '2天/周',
                                                '3': '3天/周',
                                                '4': '4天/周',
                                                '5': '5天/周'}},
            'workstate':             {'title': '工作状态',
                                      'value': {'0': '',
                                                '1': '在职，看看新机会',
                                                '2': '在职，急寻新工作',
                                                '3': '在职，暂无跳槽打算',
                                                '4': '离职，正在找工作',
                                                '5': '应届毕业生'}}}
        :param config_cv_tpls:
        :return:
        """

        # 有 kv mapping 的字段
        records = [ObjectDict(r) for r in config_cv_tpls if
                   r.get('field_value')]
        kvmappinp_ret = ObjectDict()
        for record in records:
            value_list = re.split(',|:', record.field_value)
            value = {}
            index = 0
            while True:
                try:
                    if value_list[index] and value_list[index + 1]:
                        value.update(
                            {value_list[index + 1]: value_list[index]})
                        index += 2
                except Exception:
                    break
            value.update({'0': ''})

            kvmappinp_ret.update({
                record.field_name: {
                    "title": record.field_title,
                    "value": value}
            })
            return kvmappinp_ret

    @gen.coroutine
    def custom_kvmapping(self, others_json):
        """
        把 profile others 字段中的 key 转换为 value, 供模板使用
        :param others_json
        :return:
        others:{
            "iter_others":[["学历", "本科"], ["城市", "佛山"]....],
            "special_others":{
                "projectexp":[
                    "start": "2015-06"
                    ...
                ],
                "awards":[
                    ...
                ]
            }
        }
        """
        # 自定义字段中的符复合字段
        CV_OTHER_SPECIAL_KEYS = [
            "recentjob", "schooljob", "education", "reward", "language",
            "competition", "workexp", "projectexp", "internship", "industry",
            "position", "IDPhoto"]

        # 这些字段虽然是复合字段，但是需要在发给 hr 的邮件中被当成普通字段看待
        CV_OTHER_SPECIAL_ITER_KEYS = [
            "reward", "language", "competition", "industry", "position"]

        config_cv_tpls = yield self.config_sys_cv_tpl_ds.get_config_sys_cv_tpls(
            conds={'disable': const.OLD_YES},
            fields=['field_name', 'field_title', 'map', 'field_value']
        )

        # 先找出那哪些自定义字段需要做 kvmapping
        kvmap = yield self.custom_fields_need_kvmapping(config_cv_tpls)

        others = ObjectDict()
        iter_others = []
        special_others = {}

        for key, value in purify(others_json):
            if key == "picUrl":
                # because we already have IDPhoto as key
                continue
            if key in CV_OTHER_SPECIAL_KEYS:
                special_others[key] = value
            else:
                iter_other = list()
                iter_other.append(kvmap.get(key, {}).get("title", ""))
                if kvmap.get(key, {}).get("value"):
                    iter_other.append(
                        kvmap[key].get("value").get(str(value), ""))
                else:
                    iter_other.append(value)
                iter_others.append(iter_other)

            display_name_mapping = {
                e.get('field_name'): e.get('field_title')
                for e in config_cv_tpls
            }

            # 将部分 special_keys 转为iter_others
            if key in CV_OTHER_SPECIAL_ITER_KEYS:
                iter_other = []
                if isinstance(value, list) and len(value) > 0:
                    iter_other.append(display_name_mapping.get(key))
                    msg = " ".join(value)
                    iter_other.append(msg)
                if key == "industry" and value:
                    # 期望工作行业，存储为字典值，需要处理为具体的行业名称
                    iter_other.append(display_name_mapping.get(key))
                    iter_other.append(kvmap.get(key).get('value').get(value))
                elif key == "position" and value:
                    # 期望职能
                    iter_other.append(display_name_mapping.get(key))
                    iter_other.append(value)
                iter_others.append(iter_other)

        others.iter_others = iter_others
        others.special_others = special_others
        return others

#
# from tornado.testing import AsyncTestCase, gen_test, main
# from service.data.config.config_sys_cv_tpl import ConfigSysCvTplDataService
# from pprint import pprint
# import re
#
#
# class TestKVMapping(AsyncTestCase):
#
#     @gen_test
#     def test_custom_fields_need_kvmapping(self):
#         config_sys_cv_tpl_ds = ConfigSysCvTplDataService()
#         config_cv_tpls = yield config_sys_cv_tpl_ds.get_config_sys_cv_tpls(
#             conds={'disable': const.OLD_YES},
#             fields=['field_name', 'field_title', 'map', 'field_value']
#         )
#         # 有 kv mapping 的字段
#         records = [ObjectDict(r) for r in config_cv_tpls if r.get('field_value')]
#         kvmappinp_ret = ObjectDict()
#         for record in records:
#             value_list = re.split(',|:', record.field_value)
#             value = {}
#             index = 0
#             while True:
#                 try:
#                     if value_list[index] and value_list[index + 1]:
#                         value.update(
#                             {value_list[index + 1]: value_list[index]})
#                         index += 2
#                 except Exception:
#                     break
#             value.update({'0': ''})
#
#             kvmappinp_ret.update({
#                 record.field_name: {
#                     "title": record.field_title,
#                     "value": value}
#             })
#         pprint(kvmappinp_ret)
#
#
# if __name__ == '__main__':
#     main()
