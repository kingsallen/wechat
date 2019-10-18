# coding=utf-8

import tornado.gen as gen
import conf.common as const

import conf.path as path
import util.tool.http_tool as http_tool
from service.data.base import DataService
from service.data.infra.infra_dict import InfraDictDataService
from util.common import ObjectDict
from requests.models import Request
from setting import settings
from globals import env
from conf.newinfra_service_conf.parsing import parsing
from conf.newinfra_service_conf.service_info import parsing_service


class InfraProfileDataService(DataService):
    @gen.coroutine
    def get_profile(self, user_id):
        params = ObjectDict(user_id=user_id)
        res = yield http_tool.http_get(path.PROFILE, params)
        return http_tool.unboxing(res)

    @gen.coroutine
    def get_profile_by_profile_id(self, profile_id):
        params = ObjectDict(id=profile_id)
        res = yield http_tool.http_get(path.PROFILE, params)
        return http_tool.unboxing(res)

    @gen.coroutine
    def get_profile_by_uuid(self, uuid):
        params = ObjectDict(uuid=uuid)
        res = yield http_tool.http_get(path.PROFILE, params)
        return http_tool.unboxing(res)

    @gen.coroutine
    def import_profile(self, type, username, password, user_id, company_id, ua=1, token=None, appid=None, unionid=None,
                       version=None, captcha=None):
        """
        从第三方导入 profile
        :param type: 必填 来源, 0:无法识别 1:51Job 2:Liepin 3:zhilian 4:linkedin 5:veryeast
        :param username: 选填（除了选择linkedin导入方式，其余都是必填） 帐号
        :param password: 选填（除了选择linkedin导入方式，其余都是必填） 密码
        :param user_id: 必填 登录用户的编号
        :param ua: 必填 UA来源, 0:无法识别 1:微信端 2:移动浏览器 3:PC端
        :param token: 选填（除了选择linkedin导入方式是必填，其余都是选填）linkedin 网站的access_token
        :param company_id:
        :return:
        """
        params = ObjectDict(
            type=int(type),
            username=username,
            password=password,
            user_id=user_id,
            ua=int(ua),
            token=token,
            company_id=company_id,
            maimai_appid=appid,
            unionid=unionid,
            version=version,
            code=captcha
        )
        res = yield http_tool.http_post(path.PROFILE_IMPORT, params, timeout=60)
        return http_tool.unboxing(res)

    @gen.coroutine
    def create_profile(self, user_id, source=1):
        # source 默认为 1 代表微信端创建的 profile

        # ref: http://wiki.moseeker.com/profile-api.md
        params = ObjectDict(
            lang=1,  # 语言默认为中文
            source=source,
            user_id=user_id,
            disable=1
        )

        res = yield self.handle_profile_section(
            params, method="create", section="profile")
        return http_tool.unboxing(res)

    @gen.coroutine
    def has_profile(self, user_id):
        res = yield self.handle_profile_section(
            {'user_id': user_id}, method='get', section='profile')

        ret_has_profile, _ = http_tool.unboxing(res)
        return bool(ret_has_profile)

    @gen.coroutine
    def get_profile_basic(self, profile_id):
        ret = yield self.handle_profile_section(
            {'profile_id': profile_id}, 'get', 'basic')
        return http_tool.unboxing(ret)

    @gen.coroutine
    def create_profile_basic_manually(self, profile, profile_id):
        """ 老六步创建 basic
        profile": {
        "basicInfo":{"name":"汤亦蓝","birthday":"2013-08-08"},
        "gender":"1",
        "contacts":{"mobile":18058808263,"email":"panyuxin@moseeker.net"},
        "education":[{"start":"2007-04","end":"2012-08","university":"学校","diploma":"4","major":"专业"}],
        "workexp":[{"start":"2004-10","end":"2011-06","company":"1","position":"2"}],
        }
        :param profile:
        :return:
        """

        params = ObjectDict(name=profile.basicInfo.name,
                            gender=profile.gender,
                            birth=profile.basicInfo.birthday,
                            profile_id=profile_id)

        if profile.email and profile.email.strip():
            params.update(email=profile.email.strip())

        res = yield self.handle_profile_section(
            params, method="create", section="basic")
        return http_tool.unboxing(res)

    @gen.coroutine
    def create_profile_basic_custom(self, custom_cv, profile_id):
        """从自定义简历创建 basic_info 数据 """

        params = ObjectDict(
            profile_id=profile_id,
            gender=custom_cv.get("gender", 3),
            # 微信上没有修改国籍的方式, 默认为中国(43)
            nationality_code=43)

        params.update(custom_cv)

        if custom_cv.get('nationality'):
            if not custom_cv.nationality_code:
                dict_ds = InfraDictDataService()
                code = yield dict_ds.get_country_code_by(
                    params.nationality_name)
                custom_cv.nationality_code = code

        res = yield self.handle_profile_section(
            custom_cv, method="create", section="basic")

        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_basic(self, profile_id, basic):
        params = ObjectDict(
            profile_id=profile_id,
            name=basic.name,
            gender=basic.gender,
        )

        # 调整生日: 老六步生日使用 birthday, 新六步使用 birth
        birth = basic.birthday or basic.birth
        if birth:
            params.update(birth=birth)

        # 自定义简历模版中的国籍
        if basic.nationality:
            if hasattr(basic.nationality, 'strip') and basic.nationality.strip():
                params.update(nationality_name=basic.nationality.strip())

        # profile 编辑中的国籍
        if basic.nationality_name:
            if hasattr(basic.nationality_name, 'strip') and basic.nationality_name.strip():
                params.update(nationality_name=basic.nationality_name.strip())

                if not basic.nationality_code:
                    dict_ds = InfraDictDataService()
                    code = yield dict_ds.get_country_code_by(params.nationality_name)
                    basic.nationality_code = code

            if basic.nationality_code:
                if isinstance(basic.nationality_code, int):
                    params.update(nationality_code=basic.nationality_code)

        if basic.email and basic.email.strip():
            params.update(email=basic.email.strip())
        if basic.weixin and basic.weixin.strip():
            params.update(weixin=basic.weixin.strip())
        if basic.qq and basic.qq.strip():
            params.update(qq=basic.qq.strip())

        if basic.city_name is not None:
            params.update(city_name=basic.city_name)

        if basic.remarks:
            basic.self_introduction = basic.remarks

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
            "level": record.level,
            "name": record.language.strip()},
            method="create", section="language")
        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_language(self, record, profile_id):
        res = yield self.handle_profile_section({
            "id": record.id,
            "profile_id": profile_id,
            "level": record.level,
            "name": record.language.strip()
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
            "name": record.name.strip()
        }, method="create", section="skill")
        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_skill(self, record, profile_id):
        res = yield self.handle_profile_section({
            "id": record.id,
            "profile_id": profile_id,
            "name": record.name.strip()
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
                "name": record.name.strip()
            }, method="create", section="credentials")
        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_cert(self, record, profile_id):
        res = yield self.handle_profile_section(
            {
                "id": record.id,
                "profile_id": profile_id,
                "name": record.name.strip()
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
            "profile_id": profile_id,
            "company_name": record.company_name,
            "start_date": record.start_date,
            "end_date": "" if record.end_until_now else record.end_date,
            "end_until_now": record.end_until_now
        }

        if record.get('department_name') is None or not record.get('department_name').strip():
            params.update(department_name="")
        else:
            params.update(department_name=record.department_name)

        if record.get('job') is None or not record.get('job').strip():
            params.update(job="")
        else:
            params.update(job=record.job)

        if record.get('description') is None or not record.get('description').strip():
            params.update(description="")
        else:
            params.update(description=record.description)

        res = yield self.handle_profile_section(params, method="create", section="workexp")
        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_workexp(self, record, profile_id):
        # 必填项和选填项分开处理
        params = {
            "id": record.id,
            "profile_id": profile_id,
            "company_name": record.company_name,
            "start_date": record.start_date,
            "end_date": None if record.end_until_now else record.end_date,
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
            {"id": record['id']}, method="delete", section="workexp"
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
            "profile_id": profile_id,
            "college_name": record.college_name,
            "college_code": college_code,
            "degree": record.degree,
            "start_date": record.start_date,
            "end_date": "" if record.end_until_now else record.end_date,
            "end_until_now": record.end_until_now,
            "country_id": record.country_id
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
            "id": record.id,
            "profile_id": profile_id,
            "college_name": record.college_name,
            "college_code": college_code,
            "degree": record.degree,
            "start_date": record.start_date,
            "end_date": None if record.end_until_now else record.end_date,
            "end_until_now": record.end_until_now,
            "country_id": record.country_id,
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
            {"id": record['id']}, method="delete", section="education"
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
            "profile_id": profile_id,
            "name": record.name,
            "start_date": record.start_date,
            "end_date": None if record.end_until_now else record.end_date,
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
            "id": record.id,
            "profile_id": profile_id,
            "name": record.name,
            "start_date": record.start_date,
            "end_date": None if record.end_until_now else record.end_date,
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
            {"id": record['id']}, method="delete", section="projectexp")
        return http_tool.unboxing(res)

    @gen.coroutine
    def get_profile_awards(self, profile_id):
        res = yield self.handle_profile_section(
            {"profile_id": profile_id}, method="get", section="awards")
        return http_tool.unboxing(res)

    @gen.coroutine
    def create_profile_awards(self, record, profile_id):
        res = yield self.handle_profile_section({
            "profile_id": profile_id,
            "name": record.name.strip(),
            "reward_date": record.reward_date,
        }, method="create", section="awards")
        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_awards(self, record, profile_id):
        res = yield self.handle_profile_section({
            "id": record.id,
            "profile_id": profile_id,
            "name": record.name.strip(),
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
            "id": record.id,
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
            {"id": record['id']}, method="delete", section="works")
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
            params.update({"city": record.city_name})
        if record.get('position_name'):
            for item in record.get('position_name'):
                index = 0
                params.update({"positions[{}]position_name".format(index): item.get("position_name")})
                params.update({"positions[{}]position_code".format(index): item.get("position_code")})
                index += 1
        if record.get('worktype'):
            params.update({"worktype": record.worktype})
        if record.get('salary_code'):
            params.update({"salary_code": record.salary_code})
        if record.get('industry'):
            for item in record.get('industry'):
                index = 0
                params.update({"industries[{}]industry_name".format(index): item.get("industry_name")})
                params.update({"industries[{}]industry_code".format(index): item.get("industry_code")})
                index += 1
        if record.get('workstate'):
            params.update({"workstate": record.workstate})

        res = yield self.handle_profile_section(
            params, method="create", section="intention")
        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_intention(self, record, profile_id):
        params = {
            "id": record.id,
            "profile_id": profile_id
        }
        if record.get('city_name'):
            params.update({"city": record.city_name})
        if record.get('position'):
            for item in record.get('position'):
                index = 0
                params.update({"positions[{}]position_name".format(index) : item.get("position_name")})
                params.update({"positions[{}]position_code".format(index) : item.get("position_code")})
                index += 1
        if record.get('worktype'):
            params.update({"worktype": record.worktype})
        if record.get('salary_code'):
            params.update({"salary_code": record.salary_code})
        if record.get('industry'):
            for item in record.get('industry'):
                index = 0
                params.update({"industries[{}]industry_name".format(index) : item.get("industry_name")})
                params.update({"industries[{}]industry_code".format(index) : item.get("industry_code")})
                index += 1
        if record.get('workstate'):
            params.update({"workstate": record.workstate})

        self.logger.debug("update_profile:param======>{}".format(params))

        res = yield self.handle_profile_section(
            params, method="update", section="intention")
        return http_tool.unboxing(res)

    @gen.coroutine
    def delete_profile_intention(self, record):
        res = yield self.handle_profile_section(
            {"id": record['id']}, method="delete", section="intention")
        return http_tool.unboxing(res)

    @gen.coroutine
    def get_profile_other(self, profile_id):
        res = yield self.handle_profile_section(
            {"profile_id": profile_id}, method="get", section="other")
        return http_tool.unboxing(res)

    @gen.coroutine
    def create_profile_other(self, record, profile_id):
        params = {"profile_id": profile_id}
        params.update(record)
        res = yield self.handle_profile_section(
            params, method="create", section="other")
        return http_tool.unboxing(res)

    @gen.coroutine
    def update_profile_other(self, record):
        res = yield self.handle_profile_section(
            record, method="update", section="other")
        return http_tool.unboxing(res)

    @gen.coroutine
    def handle_profile_section(self, params, method=None, section=None):
        """修改 profile 部分数据的底层方法，
        对应CRUD的method参数为 get, create, update, delete
        对应的 HTTP 动词为 GET, POST, PUT, DELETE

        profile section 标记字符串 (大小写不限)：
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
        OTHER
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
            response = yield http_tool.http_get(route, params, timeout=3)
        elif method == "create":
            response = yield http_tool.http_post(route, params, timeout=3)
        elif method == "update":
            response = yield http_tool.http_put(route, params, timeout=3)
        elif method == "delete":
            response = yield http_tool.http_delete(route, params, timeout=3)
        else:
            raise Exception('Unknow Exception')
        return response

    @gen.coroutine
    def get_linkedin_token(self, params):
        """
        获得 linkedin 的 access_token
        referer: https://developer.linkedin.com/docs/oauth2
        :param params:
        :return:
        """

        response = yield http_tool.http_fetch(path.LINKEDIN_ACCESSTOKEN, params, timeout=20, raise_error=False)
        return response

    @gen.coroutine
    def resume_upload(self, file_name, file_data, user_id):
        url = "{0}/{1}".format(settings['infra'], path.PROFILE_FILE_PARSER)
        ret = yield self.upload_file(file_name, file_data, user_id, url)
        return ret

    @gen.coroutine
    def upload_file(self, file_name, file_data, user_id, url):
        # requests的包不支持中文名文件上传，因此file_name单独传个字段
        request = Request(data={
            "user": user_id,
            "appid": const.APPID[env],
            "file_name": file_name
        },
            files={
                "file": ("", file_data)
            },
            url=url,
            method="POST"
        )
        p = request.prepare()
        body = p.body
        headers = p.headers

        ret = yield http_tool.http_post_multipart_form(url, body, headers=headers)
        return ret

    @gen.coroutine
    def get_custom_metadata(self, company_id=0, select_all=False) -> list:
        """获取自定义字段元表数据"""
        resposne = yield http_tool.http_get(path.PROFILE_OTHER_METADATA,
                                            {"companyId": company_id, "selectAll": select_all})
        _, data = http_tool.unboxing(resposne)

        return sorted(data, key=lambda x: x['id'])

    @gen.coroutine
    def infra_submit_upload_profile(self, params, user_id):
        """上传的简历提交"""
        res = yield http_tool.http_post(path.PROFILE_UPLOAD.format(user_id), params)
        return res

    @gen.coroutine
    def infra_submit_upload_profile_from_chatbot(self, params, employee_id):
        return (yield http_tool.http_post(path.PROFILE_UPLOAD_FROM_CHATBOT.format(employee_id), params))

    @gen.coroutine
    def get_uploaded_profile(self, employee_id):
        return (yield http_tool.http_get(path.PROFILE_UPLOAD_FROM_CHATBOT.format(employee_id)))

    @gen.coroutine
    def infra_is_resume_upload_complete(self, params):
        """询问上传助手小助手简历是否上传完成"""
        res = yield http_tool.http_get(path.RESUME_UPLOAD_COMPLETE, params)
        return res

    @gen.coroutine
    def infra_referral_upload_resume_info(self, params):
        """获取上传助手小程序上传的简历信息"""
        res = yield http_tool.http_get(path.REFERRAL_UPLOAD_RESUME_INFO, params)
        return res

    @gen.coroutine
    def infra_upload_miniapp_access(self, params):
        """获取上传助手小程序access_token"""
        res = yield http_tool.http_get('{}/{}'.format(settings['upload_resume_miniapp_url'], path.UPLOAD_MINIAPP_ACCESSTOKEN), params, infra=False)
        return res

    @gen.coroutine
    def custom_parse_idcard(self, file_id, side, company_id, sysuser_id):
        params = ObjectDict({
            "file_id": file_id,
            "side": side,
            "company_id": company_id,
            "user_id": sysuser_id
        })
        ret = yield http_tool.http_post_v2(parsing.INFRA_CUSTOM_PARSE_IDCARD, parsing_service, params)
        raise gen.Return(ret)
