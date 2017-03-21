# coding=utf-8

import tornado.gen as gen
from tornado.escape import json_decode, json_encode

from service.page.base import PageService
from service.page.application.application import ApplicationPageService
import conf.common as const
from util.common import ObjectDict
from util.tool.date_tool import curr_datetime_now
from datetime import datetime


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

        other_json = profile.other[0]
        if other_json:
            application_ps = ApplicationPageService()
            sys_cv_tpls = yield application_ps.get_custom_tpl_all()
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
            return None

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
