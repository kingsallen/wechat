# coding=utf-8

import tornado.gen as gen

import conf.path as path
from service.data.base import DataService
from util.common import ObjectDict
import util.tool.http_tool as http_tool


class InfraProfileDataService(DataService):

    @gen.coroutine
    def get_profile(self, user_id):
        params = ObjectDict(user_id=user_id)
        res = yield http_tool.http_get(path.PROFILE, params)
        return http_tool.unboxing(res)

    @gen.coroutine
    def import_profile(self, source, username, password, user_id):
        params = ObjectDict(
            source=source,
            username=username,
            password=password,
            user_id=user_id
        )
        res = yield http_tool.http_post(path.PROFILE_IMPORT, params, timeout=60)
        return http_tool.unboxing(res)

    @gen.coroutine
    def create_profile(self, user_id):
        # source 默认为 1 代表微信端创建的 profile
        # ref: http://wiki.moseeker.com/profile-api.md
        source = 1

        params = ObjectDict(
            lang=1,  # 语言默认为中文
            source=source,  # 标记为来自手机端
            user_id=user_id,
            disable=1
        )

        res = yield self.handle_profile_section(
            params, method="create", section="profile")
        return http_tool.unboxing(res)

    @gen.coroutine
    def get_profile_basic(self, profile_id):
        ret = yield self.handle_profile_section(
            {'profile_id': profile_id}, 'get', 'basic')
        return http_tool.unboxing(ret)

    @gen.coroutine
    def update_profile_basic(self, profile_id, basic):
        # TODO tangyiliang 现在自定义简历和常规 profile basic 更新混在一起，最好分开
        params = ObjectDict(
            profile_id=profile_id,
            name=basic.name,
            gender=basic.gender,
        )

        # 调整生日: 老六步生日使用 birthday, 新六步使用 birth
        birth = basic.birthday or basic.birth
        if birth:
            params.update(birth=birth)

        # 自定义简历模版中的字段
        if basic.nationality and basic.nationality.strip():
            params.update(nationality_name=basic.nationality.strip())
        if basic.email and basic.email.strip():
            params.update(email=basic.email.strip())
        if basic.weixin and basic.weixin.strip():
            params.update(weixin=basic.weixin.strip())
        if basic.qq and basic.qq.strip():
            params.update(qq=basic.qq.strip())

        if basic.location:
            basic.city_name = basic.location
            basic.pop('location')
        if basic.city_name is not None:
            params.update(city_name=basic.city_name)

        if basic.remarks:
            basic.self_introduction = basic.remarks
            basic.pop('remarks')
        if basic.self_introduction is not None:
            if basic.self_introduction.strip() == "":
                params.update(self_introduction="")
            else:
                params.update(self_introduction=basic.self_introduction)

        if basic.motto is not None:
            if basic.motto.strip() == "":
                params.update(motto="")
            else:
                params.update(motto=basic.motto)

        self.logger.debug("params:{}".format(params))

        res = yield self.handle_profile_section(
            params, method="update", section="basic")

        return http_tool.unboxing(res)

    @gen.coroutine
    def get_profile_language(self, profile_id):
        res = yield self.handle_profile_section(
            {'profile_id': profile_id}, 'get', 'language')
        return http_tool.unboxing(res)

    @gen.coroutine
    def create_profile_language(self, record, profile_id):
        res = yield self.handle_profile_section({
            "profile_id": profile_id,
            "level":      record.level,
            "name":       record.language.strip()},
            method="create", section="language")
        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_language(self, record, profile_id):
        res = yield self.handle_profile_section({
                "id":         record.id,
                "profile_id": profile_id,
                "level":      record.level,
                "name":       record.language.strip()
            }, method="update", section="language")
        return http_tool.unboxing(res)

    # noinspection PyUnusedLocal
    @gen.coroutine
    def delete_profile_language(self, record, profile_id=None):
        res = yield self.handle_profile_section(
            {"id": record.id}, method="delete", section="language")
        return http_tool.unboxing(res)

    @gen.coroutine
    def get_profile_skill(self, profile_id):
        res = yield self.handle_profile_section(
            {"profile_id": profile_id}, method="get", section="skill")
        return http_tool.unboxing(res)

    @gen.coroutine
    def create_profile_skill(self, record, profile_id):
        res = yield self.handle_profile_section({
                "profile_id": profile_id,
                "name":       record.name.strip()
            }, method="create", section="skill")
        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_skill(self, record, profile_id):
        res = yield self.handle_profile_section({
                "id":         record.id,
                "profile_id": profile_id,
                "name":       record.name.strip()
            }, method="update", section="skill")
        return http_tool.unboxing(res)

    # noinspection PyUnusedLocal
    @gen.coroutine
    def delete_profile_skill(self, record, profile_id):
        res = yield self.handle_profile_section(
            {"id": record.id}, method="delete", section="skill")
        return http_tool.unboxing(res)

    @gen.coroutine
    def get_profile_cert(self, profile_id):
        res = yield self.handle_profile_section(
            {"profile_id": profile_id}, method="get", section="credentials")
        return http_tool.unboxing(res)

    @gen.coroutine
    def create_profile_cert(self, record, profile_id):
        res = yield self.handle_profile_section(
            {
                "profile_id": profile_id,
                "name":       record.name.strip()
            }, method="create", section="credentials")
        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_cert(self, record, profile_id):
        res = yield self.handle_profile_section(
            {
                "id":         record.id,
                "profile_id": profile_id,
                "name":       record.name.strip()
            }, method="update", section="credentials")
        return http_tool.unboxing(res)

    # noinspection PyUnusedLocal
    @gen.coroutine
    def delete_profile_cert(self, record, profile_id):
        res = yield self.handle_profile_section(
            {"id": record.id}, method="delete", section="credentials")
        return http_tool.unboxing(res)

    @gen.coroutine
    def get_profile_workexp(self, workexp_id):
        ret = yield self.handle_profile_section(
            {"id": workexp_id}, method="get", section="workexp")
        return http_tool.unboxing(ret)

    @gen.coroutine
    def create_profile_workexp(self, record, profile_id):
        # 必填项和选填项分开处理
        params = {
            "profile_id":    profile_id,
            "company_name":  record.company_name,
            "start_date":    record.start_date,
            "end_date":      None if record.end_until_now else record.end_date,
            "end_until_now": record.end_until_now
        }
        if record.get('department_name') is None or \
            not record.get('department_name').strip():
            params.update(department_name="")
        else:
            params.update(department_name=record.department_name)

        if record.get('job') is None or not record.get('job').strip():
            params.update(job="")
        else:
            params.update(job=record.job)

        if record.get('description') is None or \
            not record.get('description').strip():
            params.update(description="")
        else:
            params.update(description=record.description)

        res = yield self.handle_profile_section(params, method="create",
                                                 section="workexp")
        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_workexp(self, record, profile_id):
        # 必填项和选填项分开处理
        params = {
            "id":            record.id,
            "profile_id":    profile_id,
            "company_name":  record.company_name,
            "start_date":    record.start_date,
            "end_date":      None if record.end_until_now else record.end_date,
            "end_until_now": record.end_until_now
        }
        if record.get('department_name') is None or \
            not record.get('department_name').strip():
            params.update(department_name="")
        else:
            params.update(department_name=record.department_name)

        if record.get('job') is None or not record.get('job').strip():
            params.update(job="")
        else:
            params.update(job=record.job)

        if record.get('description') is None or not record.get(
            'description').strip():
            params.update(description="")
        else:
            params.update(description=record.description)

        res = yield self.handle_profile_section(
            params, method="update", section="workexp")

        return http_tool.unboxing(res)

    @gen.coroutine
    def delete_profile_workexp(self, record, profile_id):
        res = yield self.handle_profile_section(
            {"id": record.id}, method="delete", section="workexp"
        )
        return http_tool.unboxing(res)

    @gen.coroutine
    def get_profile_education(self, education_id):
        res = yield self.handle_profile_section(
            {"id": education_id}, method="get", section="education")
        return http_tool.unboxing(res)

    @gen.coroutine
    def create_profile_education(self, record, profile_id, college_code):
        # 必填项和选填项分开处理
        params = {
            "profile_id":    profile_id,
            "college_name":  record.college_name,
            "college_code":  college_code,
            "degree":        record.degree,
            "start_date":    record.start_date,
            "end_date":      None if record.end_until_now else record.end_date,
            "end_until_now": record.end_until_now,
        }

        if record.get("major_name") is None or not record.get(
            "major_name").strip():
            params.update(major_name="")
        else:
            params.update(major_name=record.major_name)

        if record.get("description") is None or not record.get(
            "description").strip():
            params.update(description="")
        else:
            params.update(description=record.description)

        if record.get('logo') is None or not record.get("logo").strip():
            params.update(college_logo="")
        else:
            params.update(college_logo=record.logo)

        res = yield self.handle_profile_section(
            params, method="create", section="education")

        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_education(self, record, profile_id, college_code):
        # 必填项和选填项分开处理
        params = {
            "id":            record.id,
            "profile_id":    profile_id,
            "college_name":  record.college_name,
            "college_code":  college_code,
            "degree":        record.degree,
            "start_date":    record.start_date,
            "end_date":      None if record.end_until_now else record.end_date,
            "end_until_now": record.end_until_now,
        }

        if record.get("major_name") is None or not record.get(
            "major_name").strip():
            params.update(major_name="")
        else:
            params.update(major_name=record.major_name)

        if record.get("description") is None or not record.get(
            "description").strip():
            params.update(description="")
        else:
            params.update(description=record.description)

        if record.get('logo') is None or not record.get("logo").strip():
            params.update(college_logo="")
        else:
            params.update(college_logo=record.logo)

        res = yield self.handle_profile_section(
            params, method="update", section="education")

        return http_tool.unboxing(res)

    @gen.coroutine
    def delete_profile_education(self, record, profile_id):
        res = yield self.handle_profile_section(
            {"id": record.id}, method="delete", section="education"
        )
        return http_tool.unboxing(res)

    @gen.coroutine
    def get_profile_projectexp(self, projectexp_id):
        res = yield self.handle_profile_section(
            {"id": projectexp_id}, method="get", section="projectexp")
        return http_tool.unboxing(res)

    @gen.coroutine
    def create_profile_projectexp(self, record, profile_id):
        params = {
            "profile_id":    profile_id,
            "name":          record.name,
            "start_date":    record.start_date,
            "end_date":      None if record.end_until_now else record.end_date,
            "end_until_now": record.end_until_now
        }

        if record.get("company_name") is not None:
            params.update(company_name=record.company_name)

        if record.get("description") is not None:
            params.update(description=record.description.strip())

        res = yield self.handle_profile_section(
            params, method="create", section="projectexp")
        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_projectexp(self, record, profile_id):
        params = {
            "id":            record.id,
            "profile_id":    profile_id,
            "name":          record.name,
            "start_date":    record.start_date,
            "end_date":      None if record.end_until_now else record.end_date,
            "end_until_now": record.end_until_now
        }

        if record.get("company_name") is not None:
            params.update(company_name=record.company_name)

        if record.get("description") is not None:
            params.update(description=record.description.strip())

        res = yield self.handle_profile_section(
            params, method="update", section="projectexp")
        return http_tool.unboxing(res)

    @gen.coroutine
    def delete_profile_projectexp(self, record, profile_id):
        res = yield self.handle_profile_section(
            {"id": record.id}, method="delete", section="projectexp")
        return http_tool.unboxing(res)

    @gen.coroutine
    def get_profile_awards(self, profile_id):
        res = yield self.handle_profile_section(
            {"profile_id": profile_id}, method="get", section="awards")
        return http_tool.unboxing(res)

    @gen.coroutine
    def create_profile_awards(self, record, profile_id):
        res = yield self.handle_profile_section({
                "profile_id":  profile_id,
                "name":        record.name.strip(),
                "reward_date": record.reward_date,
            }, method="create", section="awards")
        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_awards(self, record, profile_id):
        res = yield self.handle_profile_section({
                "id":          record.id,
                "profile_id":  profile_id,
                "name":        record.name.strip(),
                "reward_date": record.reward_date,
            }, method="update", section="awards")
        return http_tool.unboxing(res)

    @gen.coroutine
    def delete_profile_awards(self, record, profile_id):
        res = yield self.handle_profile_section(
            {"id": record.id}, method="delete", section="awards")
        return http_tool.unboxing(res)

    @gen.coroutine
    def get_profile_works(self, works_id):
        res = yield self.handle_profile_section(
            {"id": works_id}, method="get", section="works")
        return http_tool.unboxing(res)

    @gen.coroutine
    def create_profile_works(self, record, profile_id):
        # 必填项和选填项分开处理
        # 然而 works 没有必填项

        params = {"profile_id": profile_id}

        if record.get('cover') is not None:
            params.update(cover=record.cover)

        if record.get('url') is not None:
            params.update(url=record.url)

        if record.get('description') is not None:
            params.update(description=record.description)

        res = yield self.handle_profile_section(
            params, method="create", section="works")
        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_works(self, record, profile_id):
        # 必填项和选填项分开处理
        # 然而 works 没有必填项

        params = {
            "id":         record.id,
            "profile_id": profile_id,
        }

        if record.get('cover') is None or record.get('cover').strip() == "":
            params.update(cover="")
        else:
            params.update(cover=record.cover)

        if record.get('url') is None or record.get('url').strip() == "":
            params.update(url="")
        else:
            params.update(url=record.url)

        if record.get('description') is None or \
                record.get('description').strip() == "":
            params.update(description="")
        else:
            params.update(description=record.description)

        res = yield self.handle_profile_section(
            params, method="update", section="works")
        return http_tool.unboxing(res)

    @gen.coroutine
    def delete_profile_works(self, record, profile_id):
        res = yield self.handle_profile_section(
            {"id": record.id}, method="delete", section="works")
        return http_tool.unboxing(res)

    @gen.coroutine
    def get_profile_intention(self, intention_id):
        res = yield self.handle_profile_section(
            {"id": intention_id}, method="get", section="intention")
        return http_tool.unboxing(res)

    @gen.coroutine
    def create_profile_intention(self, record, profile_id):
        params = {"profile_id": profile_id}
        if record.get('city_name'):
            params.update({"cities[0]city_name": record.city_name})
        if record.get('position_name'):
            params.update({"positions[0]position_name": record.position_name})
        if record.get('worktype'):
            params.update({"worktype": record.worktype})
        if record.get('salary_code'):
            params.update({"salary_code": record.salary_code})

        res = yield self.handle_profile_section(
            params, method="create", section="intention")
        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_intention(self, record, profile_id):
        params = {
            "id":         record.id,
            "profile_id": profile_id
        }
        if record.get('city_name'):
            params.update({"cities[0]city_name": record.city_name})
        if record.get('position_name'):
            params.update({"positions[0]position_name": record.position_name})
        if record.get('worktype'):
            params.update({"worktype": record.worktype})
        if record.get('salary_code'):
            params.update({"salary_code": record.salary_code})

        res = yield self.handle_profile_section(
            params, method="update", section="intention")
        return http_tool.unboxing(res)

    @gen.coroutine
    def delete_profile_intention(self, record, profile_id):
        res = yield self.handle_profile_section(
            {"id": record.id}, method="delete", section="intention")
        return http_tool.unboxing(res)

    @gen.coroutine
    def handle_profile_section(self, params, method=None, section=None):
        """修改 profile 部分数据的底层方法，
        对应CRUD的method参数为 get, create, update, delete
        对应的 HTTP 动词为 GET, POST, PUT, DELETE

        profile 部分标记字符串 (大小写不限)：
        BASIC
        LANGUAGE
        SKILL
        CREDENTIALS
        EDUCATION
        PROFILE
        WORKEXP
        PROJECTEXP
        AWARDS
        WORKS
        INTENTION
        """
        try:
            if not method or not section:
                raise ValueError
            assert method in ['get', 'create', 'update', 'delete']
            route = getattr(path, ("profile_" + section).upper())
        except:
            raise ValueError('Invalid method or section')

        # 基础服务（大飞）要求，将 params 中 value 为 None 的剔除掉，
        params = {k: v for k, v in params.items() if v is not None}

        if method == "get":
            response = yield http_tool.http_get(route, params)
        elif method == "create":
            response = yield http_tool.http_post(route, params)
        elif method == "update":
            response = yield http_tool.http_put(route, params)
        elif method == "delete":
            response = yield http_tool.http_delete(route, params)
        else:
            raise Exception('Unknow Exception')
        return response
