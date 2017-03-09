# coding=utf-8

import tornado.gen as gen

from service.page.base import PageService
from util.common import ObjectDict
from util.tool.date_tool import curr_datetime_now

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
    def get_profile_basic(self, profile_id):
        result, data = yield self.infra_profile_ds.get_profile_basic(
            profile_id)
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
    def create_profile_workexp(self, record, profile_id):
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

    # @gen.coroutine
    # def create_profile_projectexp(self, record, profile_id):
    #     college_code = yield self.infra_dict_ds.get_college_code_by_name(
    #         record.college_name)
    #     result, data = yield self.infra_profile_ds.create_profile_projectexp(
    #         record, profile_id, college_code)
    #     return result, data
    #
    # @gen.coroutine
    # def update_profile_projectexp(self, record, profile_id):
    #     college_code = yield self.infra_dict_ds.get_college_code_by_name(
    #         record.college_name)
    #     result, data = yield self.infra_profile_ds.update_profile_projectexp(
    #         record, profile_id, college_code)
    #     return result, data
    #
    # @gen.coroutine
    # def delete_profile_projectexp(self, record, profile_id):
    #     result, data = yield self.infra_profile_ds.delete_profile_projectexp(
    #         record, profile_id)
    #     return result, data

    def calculate_workyears(p_workexps):
        """
        :param p_workexps:
        :return:
        """
        min_start_date = None
        max_end_date = None
        until_now = False
        workyears = 0
        try:
            for workexp in p_workexps:
                if (min_start_date is None or
                            min_start_date > workexp.get("start_date")):
                    min_start_date = workexp.get("start_date")

                if (max_end_date is None or
                            max_end_date < workexp.get("end_date")):
                    max_end_date = workexp.get("end_date")

                if not until_now and workexp.get("end_until_now"):
                    until_now = workexp.get("end_until_now")

            if until_now:
                max_end_date = curr_datetime_now().year
            else:
                max_end_date = max_end_date[:4]
            workyears = (int(max_end_date) - int(min_start_date[:4]))
        except Exception as e:
            workyears = 0
        finally:
            return workyears

    def get_job_for_application(self, profile):
        """
        获取最新的工作经历用以申请
        """
        if not profile.get("workexps", []):
            return None

        if self.has_current_job(profile):
            return self.get_current_job(profile)

        return self.get_latest_job(profile)

    def has_current_job(self, profile):
        """
        判断 profile 是否包含"含有至今"的工作信息
        """
        wexps = profile.get('workexps', [])
        if wexps:
            return (len(filter(
                lambda w: w.get("end_until_now", 0) == 1, wexps)) > 0)
        return False

    def get_current_job(self, profile):
        """
        获取 profile 中最新的一条"含有至今"的工作信息
        """
        wexps = profile.get('workexps', [])

        latest_jobs = filter(lambda w: w.get("end_until_now", 0) == 1, wexps)
        return (sorted(latest_jobs, key=lambda x: x.get("start_date", ""),
                       reverse=True)[0])

    def get_latest_job(self, profile):
        """
        获取最新的一条工作记录
        """
        wexps = profile.get('workexps', [])
        return (sorted(wexps, key=lambda x: x.get('start_date', ""),
                       reverse=True)[0])

