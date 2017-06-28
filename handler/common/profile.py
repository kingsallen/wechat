# coding=utf-8

import tornado
import tornado.gen
from tornado.escape import json_decode, json_encode

import conf.common as const
import conf.message as msg
import conf.path as path
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, check_and_apply_profile, \
    authenticated
from util.tool.dict_tool import sub_dict, objectdictify
from util.tool.str_tool import mobile_validate

class ProfileNewHandler(BaseHandler):

    @handle_response
    @authenticated
    @tornado.gen.coroutine
    def get(self):
        """初始化新建 profile 页面"""

        data = ObjectDict()
        data.email = self.current_user.sysuser.email or ''
        data.mobile = self.current_user.sysuser.mobile or ''
        data.degreeList = yield self.dictionary_ps.get_degrees()
        self.send_json_success(data=data)

    @handle_response
    @authenticated
    @tornado.gen.coroutine
    def post(self):

        profile = ObjectDict(json_decode(self.request.body)).profile

        # 姓名必填
        if not profile.basicInfo or not profile.basicInfo.name:
            message = "".join([msg.PROFILE_REQUIRED_HINT_HEAD, "姓名", msg.PROFILE_REQUIRED_HINT_TAIL])
            self.send_json_error(message=message)
            return

        # 手机号必填
        if not profile.contacts or not profile.contacts.get('mobile', None):
            message = "".join([msg.PROFILE_REQUIRED_HINT_HEAD, "手机号", msg.PROFILE_REQUIRED_HINT_TAIL])
            self.send_json_error(message=message)
            return

        # 手机号格式验证
        if not mobile_validate(profile.contacts.get('mobile', None)):
            message = "手机号码格式不正确"
            self.send_json_error(message=message)
            return

        yield self.user_ps.update_user(
            self.current_user.sysuser.id,
            name=profile.basicInfo['name'],
            email=profile.contacts['email'],
            mobile=profile.contacts['mobile'])

        basic_info_ok = False
        education_ok = True
        workexp_ok = True

        # 判断是否来自企业号，聚合号, 还是移动网页端
        if not self.in_wechat:
            source = const.PROFILE_SOURCE_MOBILE_BROWSER
        else:
            if self.is_platform:
                source = const.PROFILE_SOURCE_PLATFORM
            else:
                source = const.PROFILE_SOURCE_QX

        # create Profile
        result, data = yield self.profile_ps.create_profile(self.current_user.sysuser.id, source)

        if result:
            profile_id = data
            profile_ok = True
            self.debug("profile_profile created with id: %s" % profile_id)
            self._log_customs.update(new_profile=const.YES)
        else:
            self.logger.error("profile_profile creation failed. res:{}".format(data))
            self.send_json_error()
            return

        self.debug("[profile post]profile:{}".format(profile))

        result, data = yield self.profile_ps.create_profile_basic(profile, profile_id)
        if result:
            basic_info_ok = True
            self.debug("profile_basic created, id: %s" % data)
        else:
            self.logger.error("profile_basic creation failed. res: %s" % data)

        self.debug("[profile post]create_profile_basic result:{}".format(result))
        self.debug("[profile post]create_profile_basic data:{}".format(data))

        for edu in profile.education:
            self.debug("[profile post]profile.education edu:{}".format(edu))
            result, data = yield self.profile_ps.create_profile_education(ObjectDict(edu), profile_id)
            if result:
                self.debug("profile_education creation passed. New record num: %s" % data)
            else:
                education_ok = False
                self.logger.error("profile_education creation failed. res: %s" % data)
                break

        self.debug("[profile post]create_profile_education result:{}".format(result))
        self.debug("[profile post]create_profile_education data:{}".format(data))

        for wxp in profile.workexp:
            self.debug("[profile post]profile.workexp wxp:{}".format(wxp))
            result, data = yield self.profile_ps.create_profile_workexp(ObjectDict(wxp), profile_id)
            if result:
                self.debug("profile_work_exp creation passed. New record num: %s" % data)
            else:
                workexp_ok = False
                self.logger.error("profile_work_exp creation failed. res: %s" % data)
                break

        self.debug("[profile post]create_profile_workexp result:{}".format(result))
        self.debug("[profile post]create_profile_workexp data:{}".format(data))

        # 只有全部 ok 后才可以跳转
        if profile_ok and basic_info_ok and education_ok and workexp_ok:
            dqpid = self.get_cookie('dqpid')
            self.debug('dqpid: %s' % dqpid)
            if dqpid:
                next_url = self.make_url(path.PROFILE_PREVIEW, self.params, pid=str(dqpid))
            else:
                next_url = self.make_url(path.PROFILE_VIEW, self.params)
            self.debug('next_url: %s' % next_url)
            self.clear_cookie(name='dqpid')
            self.send_json_success(data=ObjectDict(next_url=next_url))
        else:
            self.send_json_warning(message='profile created partially')


class ProfilePreviewHandler(BaseHandler):

    @handle_response
    @check_and_apply_profile
    @authenticated
    @tornado.gen.coroutine
    def get(self):
        if not self.params.pid:
            url = self.make_url(path.PROFILE_VIEW, self.params)
            self.redirect(url)
            return

        profile_tpl = yield self.profile_ps.profile_to_tempalte(
            self.current_user.profile)

        if self.current_user.sysuser.mobile:
            current_mobile = str(self.current_user.sysuser.mobile)
        else:
            current_mobile = ''

        try:
            # 只有存在 is_skip 且值为 '1' 时才跳过 preview
            is_skip = int(self.params.is_skip) == const.YES
        except Exception:
            is_skip = False

        need_mobile_validate = str(self.current_user.sysuser.mobile) != \
                               str(self.current_user.sysuser.username)

        tparams = {
            'profile':              profile_tpl,
            'pid':                  self.params.pid,
            'is_skip':              is_skip,
            'need_mobile_validate': need_mobile_validate,
            'no_name':              not bool(self.current_user.sysuser.name),
            'current_mobile':       current_mobile
        }

        self.render_page(template_name='profile/preview.html', data=tparams, meta_title=const.PROFILE_PREVIEW)

class ProfileViewHandler(BaseHandler):

    """Profile 游客页"""

    @handle_response
    @tornado.gen.coroutine
    def get(self, uuid):

        has_profile, profile = yield self.profile_ps.has_profile_by_uuid(uuid=uuid)

        if not uuid or not has_profile:
            self.write_error(404)
            return

        # 如果是用户本人，则跳转到用户可以编辑的个人档案页
        if profile.profile.user_id == self.current_user.sysuser.id:
            redirect_url = self.make_url(path=path.PROFILE_VIEW)
            self.redirect(redirect_url)
            return

        profile_tpl = yield self.profile_ps.profile_to_tempalte(profile)
        # 游客页不应该显示 other信息，求职意愿
        profile_tpl.other = ObjectDict()
        profile_tpl.job_apply = ObjectDict()

        tparams = {
            "profile": profile_tpl,
            "is_self": False,
        }

        self.params.share = self._share(uuid, profile_tpl)
        self.render_page(template_name='profile/preview.html', data=tparams, meta_title=const.PROFIEL_VIEW)

    def _share(self, uuid, profile_tpl):
        default = ObjectDict({
            'cover': self.static_url(profile_tpl.avatar_url),
            'title': '【{}】的个人职场档案'.format(profile_tpl.username),
            'description': '点击查看{}的个人职场档案'.format(profile_tpl.username),
            'link': self.make_url(path.PROFILE_VISITOR_VIEW.format(uuid), self.params)
        })

        return default

class ProfileHandler(BaseHandler):
    """ProfileHandler
    GET Profile 页面渲染
    POST 手动创建Profile -> 俗称老6步
    """

    @handle_response
    @authenticated
    @check_and_apply_profile
    @tornado.gen.coroutine
    def get(self):
        """ 查看个人 Profile
        如果有 GET 请求参数包含 pid,
        在 profile 页面吸顶显示申请按钮
        """

        profile_tpl = yield self.profile_ps.profile_to_tempalte(
            self.current_user.profile)
        self.params.share = self._share(self.current_user.profile.profile.get("uuid"), profile_tpl)
        self.render_page(template_name='profile/main.html', data=profile_tpl)

    def _share(self, uuid, profile_tpl):
        default = ObjectDict({
            'cover': self.static_url(profile_tpl.avatar_url),
            'title': '【{}】的个人职场档案'.format(profile_tpl.username),
            'description': '点击查看{}的个人职场档案'.format(profile_tpl.username),
            'link': self.make_url(path.PROFILE_VISITOR_VIEW.format(uuid), self.params)
        })

        return default


class ProfileCustomHandler(BaseHandler):
    """使用自定义简历页创建或更新profile"""

    @handle_response
    @authenticated
    @tornado.gen.coroutine
    def get(self):
        pid = int(self.params.pid)
        position = yield self.position_ps.get_position(pid)
        if not position.app_cv_config_id:
            self.write_error(404)
            return

        has_profile, profile = yield self.profile_ps.has_profile(
            self.current_user.sysuser.id)
        if has_profile:
            resume_dict = yield self.application_ps._generate_resume_cv(
                profile)
        else:
            resume_dict = {}

        json_config = yield self.application_ps.get_hr_app_cv_conf(
            position.app_cv_config_id)
        cv_conf = json_config.field_value

        self.render(
            template_name='refer/weixin/application/app_cv_conf.html',
            resume=json_encode(json_encode(resume_dict)),
            cv_conf=json_encode(cv_conf))

    @handle_response
    @authenticated
    @tornado.gen.coroutine
    def post(self):

        custom_cv = ObjectDict(json_decode(self.get_argument("_cv", "")))
        if not custom_cv:
            raise Exception("get custom_cv failed")

        yield self._save_custom_cv(custom_cv)

        p = dict()
        p.update(is_skip=(self.current_user.company.id in self.customize_ps._DIRECT_APPLY))
        self.redirect(self.make_url(path.PROFILE_PREVIEW, self.params, **p))

    @tornado.gen.coroutine
    def _save_custom_cv(self, custom_cv):

        # 更新 user 信息（非 profile 信息）
        yield self.user_ps.update_user(
            user_id=self.current_user.sysuser.id,
            mobile=custom_cv.get('mobile'),
            name=custom_cv.get('name'),
            email=custom_cv.get('email'))

        has_profile, profile = yield self.profile_ps.has_profile(
            self.current_user.sysuser.id)

        custom_cv_tpls = yield self.profile_ps.get_custom_tpl_all()
        custom_fields = [c.field_name for c in custom_cv_tpls if not c.map]

        profile_id = 0

        # 已经有 profile，更新和自定义简历联动的 profile 信息
        if has_profile:
            profile_id = profile.get("profile", {}).get("id", None)
            basic = profile.get("basic")
            basic.update(custom_cv)
            # 更新 profile_basic 表的对应字段
            yield self.profile_ps.update_profile_basic(profile_id, basic)
            # 更新 education, workexp, projectext
            yield self.profile_ps.update_profile_embedded_info_from_cv(
                profile_id, custom_cv)

        else:
            # 还不存在 profile， 创建 profile
            # 进入自定义简历创建 profile 逻辑的话，来源必定是企业号（我要投递）
            result, data = yield self.profile_ps.create_profile(
                self.current_user.sysuser.id,
                source=const.PROFILE_SOURCE_PLATFORM_APPLY)

            # 创建 profile 成功
            if result:
                profile_id = data

                cv_profile_values = {k: v for k, v in custom_cv.items() if
                                     k in custom_fields}

                self.debug('cv_profile_values: %s' % cv_profile_values)
                self._log_customs.update(new_profile=const.YES)
                # BASIC INFO
                result, data = yield self.profile_ps.create_profile_basic(
                    cv_profile_values, profile_id, mode='c')

                if result:
                    self.debug(
                        "profile_basic creation passed. Got basic info id: %s" % data)
                else:
                    self.logger.error("profile_basic creation failed. res: %s" % data)

                yield self.profile_ps.update_profile_basic(profile_id, custom_cv)
                yield self.profile_ps.update_profile_embedded_info_from_cv(
                    profile_id, custom_cv)
            else:
                raise ValueError('profile creation error')

        if profile_id:
            # profile = ObjectDict()
            # basicInfo = ObjectDict()

            # const.CUSTOM_FIELD_NAME_TO_PROFILE_FIELD
            # 为自定义字段到 profile 字段的对应

            # 如果 value 为 "",表明没有对应的 profile 字段,
            # 应该存入 profile_others
            # 因为 profile 对应字段都是属于 basic 的,所以都加入 basicInfo 中
            # 这样可以做到和老六步兼容
            #  *const.CUSTOM_FIELD_NAME_TO_PROFILE_FIELD 需要微信后端自行维护

            # 自定义简历模版提交的 picUrl 作为 IDPhoto 使用
            if custom_cv.get('picUrl'):
                custom_cv['IDPhoto'] = custom_cv.get('picUrl')

            cv_pure_custom = {k: v for k, v in custom_cv.items() if
                              k in custom_fields}

            other_string = json_encode(cv_pure_custom)
            record = ObjectDict(other=other_string)
            yield self.application_ps.update_profile_other(record, profile_id)


class ProfileSectionHandler(BaseHandler):
    """
    ProfileSectionHandler
    Profile 各部分修改 相关 Api 处理

    前后端数据传输格式
    ``` json
    {
      status: 0/1, // 0:成功， 非0:异常
      message: "", // 消息文本，前端根据 status 判断渲染样式
      data: {
        route: "", // 模块名称
        model: { // 模块所需数据
          key1: '', // 模块所需数据 1，此为举例
          key2: '', // 模块所需数据 2，此为举例
          ...,
          __status: 'o'/'x' // 仅前端往后端传递数据时存在，代表这条数据是新建还是删除。如果这条数据含有 id， 那么将这条数据视为更新
        },
        constant: { // 仅后端往前端传递数据时存在，该模块所需的常量列表
          degree_list: { // 此为学历常量的例子
            '0': '未选择',
            '1': '小学'
          }
          scale_list: {......} // 此为公司规模常量的例子
        },
        isAdd: 1 // 仅后端往前端传递数据时存在，某些复合信息(教育经历，工作经历) 以此字段判断是否是展示新建页面
      }
    }
    ```
    """

    @handle_response
    @check_and_apply_profile
    @authenticated
    @tornado.gen.coroutine
    def get(self):
        # 根据 route 跳转到不同的子方法
        yield getattr(self, "get_" + self.params.route)()
        self._log_customs.update(get_profile=const.YES,
                                 section=self.params.route)

    @handle_response
    @check_and_apply_profile
    @authenticated
    @tornado.gen.coroutine
    def post(self):
        # 根据 route 跳转到不同的子方法
        self.guarantee('route', 'model')
        yield getattr(self, "post_" + self.params.route)()
        self._log_customs.update(update_profile=const.YES,
                                 section=self.params.route)

    def _get_profile_id(self):
        try:
            profile_id = self.current_user.profile.profile.id
        except AttributeError as e:
            self.logger.error(e)
            self.logger.error('Forget to use @check_and_apply_profile?')
            raise
        else:
            return profile_id

    def _make_json_data(self, route=None, model=None, constant=None, new=False):
        try:
            assert route in self.profile_ps.FE_ROUTES.keys()
        except:
            raise ValueError('invalid component')

        data = ObjectDict(
            route=route,
            model=model,
            constant=constant
        )

        if new is True:
            data.update(isAdd=const.YES)
        return data

    # Profile 编辑 -- basic & self-introduction 开始
    @tornado.gen.coroutine
    def get_basic(self, self_intro=False):
        profile_id = self._get_profile_id()
        result, profile_basic = yield self.profile_ps.get_profile_basic(
            profile_id)
        if not result:
            raise ValueError('cannot get profile_basic')
        else:
            pass

        route = self.params.route

        if self_intro:
            model = sub_dict(profile_basic[0], 'self_introduction')
        else:
            model = sub_dict(profile_basic[0], self.profile_ps.BASIC_KEYS)

        self.send_json_success(
            data=self._make_json_data(route, model))

    @tornado.gen.coroutine
    def post_basic(self, self_intro=False):
        profile_id = self._get_profile_id()
        model = ObjectDict(self.params.model)

        if model:
            if self_intro:
                if len(model.self_introduction) > 1000:
                    self.send_json_error(message=msg.PROFILE_OVERLENGTH % "自我介绍")
                    return
                model.update(
                    self_introduction=model.self_introduction)
            else:
                model.update(sub_dict(model, self.profile_ps.BASIC_KEYS))
                model.pop('self_introduction')

                if model.city_name == "未知" or model.city_name is None:
                    model.pop('city_name')

            result, data = yield self.profile_ps.update_profile_basic(
                profile_id, model)

            if result:
                self.send_json_success()
            else:
                self.send_json_error()
        else:
            self.send_json_error(message='no component_data')

    @tornado.gen.coroutine
    def get_description(self):
        yield self.get_basic(self_intro=True)

    @tornado.gen.coroutine
    def post_description(self):
        yield self.post_basic(self_intro=True)
    # Profile 编辑 -- basic & self-introduction 结束

    # Profile 编辑 -- language 开始
    @tornado.gen.coroutine
    def get_language(self):
        route = self.params.route
        languages = self.current_user.profile.languages
        model = []
        for l in languages:
            e = sub_dict(l, self.profile_ps.LANGUAGE_KEYS)
            e.update(language=e.name)
            del e['name']
            model.append(e)

        self.send_json_success(
            data=self._make_json_data(route, model))

    @tornado.gen.coroutine
    def post_language(self):
        profile_id = self._get_profile_id()

        model = objectdictify(self.params.model)

        results = []
        for e in model:
            if hasattr(e, "__status") and getattr(e, "__status") == 'x':
                verb = "delete"
            else:
                verb = 'update' if e.id else 'create'

            result, res = yield getattr(
                self.profile_ps, verb + "_profile_language")(e, profile_id)
            results.append(result)

        self._send_json_result(results, len(model))
    # Profile 编辑 -- language 结束

    # Profile 编辑 -- skill 开始
    @tornado.gen.coroutine
    def get_skill(self):
        skills = self.current_user.profile.skills
        route = self.params.route
        model = [sub_dict(s, self.profile_ps.SKILL_KEYS) for s in skills]
        self.send_json_success(data=self._make_json_data(route, model))

    @tornado.gen.coroutine
    def post_skill(self):
        profile_id = self._get_profile_id()
        model = objectdictify(self.params.model)

        results = []
        for e in model:
            if hasattr(e, "__status") and getattr(e, "__status") == 'x':
                verb = "delete"
            else:
                verb = 'update' if e.id else 'create'

            result, res = yield getattr(
                self.profile_ps, verb + "_profile_skill")(e, profile_id)
            results.append(result)

        self._send_json_result(results, len(model))
    # Profile 编辑 -- skill 结束

    # Profile 编辑 -- cert 开始
    @tornado.gen.coroutine
    def get_cert(self):
        credentials = self.current_user.profile.credentials
        route = self.params.route
        model = [sub_dict(s, self.profile_ps.CERT_KEYS) for s in credentials]
        self.send_json_success(data=self._make_json_data(route, model))

    @tornado.gen.coroutine
    def post_cert(self):
        profile_id = self._get_profile_id()
        model = objectdictify(self.params.model)

        results = []
        for e in model:
            if hasattr(e, "__status") and getattr(e, "__status") == 'x':
                verb = "delete"
            else:
                verb = 'update' if e.id else 'create'

            result, res = yield getattr(
                self.profile_ps, verb + "_profile_cert")(e, profile_id)
            results.append(result)

        self._send_json_result(results, len(model))
    # Profile 编辑 -- cert 结束

    # Profile 编辑 -- jobexp 开始
    @tornado.gen.coroutine
    def get_jobexp(self):
        profile_id = self._get_profile_id()
        route = self.params.route

        scale_list = yield self.dictionary_ps.get_constants(
            parent_code=const.CONSTANT_PARENT_CODE.COMPANY_SCALE)
        constant = ObjectDict(scale_list=scale_list)

        model = {}
        new = False

        if not self.params.id:
            new = True
        else:
            result, data = yield self.profile_ps.get_profile_workexp(workexp_id=self.params.id)
            if result and data[0].get('profile_id') == profile_id:
                model.update(sub_dict(data[0], self.profile_ps.WORKEXP_KEYS))
            else:
                self.send_json_error()

        self.send_json_success(
            data=self._make_json_data(
                route=route, model=model, new=new,
                constant=constant))

    @tornado.gen.coroutine
    def post_jobexp(self):
        profile_id = self._get_profile_id()
        model = objectdictify(self.params.model)

        if hasattr(model, "__status") and getattr(model, "__status") == 'x':
            verb = "delete"
        else:
            if model.description and len(model.description) > 1000:
                self.send_json_error(message=msg.PROFILE_OVERLENGTH % "工作描述")
                return
            verb = 'update' if model.id else 'create'

        result, res = yield getattr(
            self.profile_ps, verb + "_profile_workexp")(
            model, profile_id, mode='p')

        if result:
            self.send_json_success()
        else:
            self.send_json_error()

    @tornado.gen.coroutine
    def post_jobexp_company(self):
        model = objectdictify(self.params.model)

        # 通过名称查询企业是否已经存在
        name = model.name
        result, res = yield self.company_ps.get_cp_for_sug_wechat(name)

        if result:
            self.send_json_error(message=msg.PROFILE_COMPANY_NAME_EXISTED)
            return
        else:
            result, res = yield self.company_ps.create_company_on_wechat(
                model)
            if result:
                self.send_json_success(message='company created')
            else:
                self.send_json_error(message='company creation error')
    # Profile 编辑 -- jobexp 结束

    # Profile 编辑 -- eduexp 开始
    @tornado.gen.coroutine
    def get_eduexp(self):
        profile_id = self._get_profile_id()
        route = self.params.route

        degree_list = yield self.dictionary_ps.get_constants(
            parent_code=const.CONSTANT_PARENT_CODE.DEGREE_USER)
        constant = {'degree_list': degree_list}

        model = {}
        new = False

        if not self.params.id:
            new = True

        else:
            result, data = yield self.profile_ps.get_profile_education(
                education_id=self.params.id)

            if result and data[0].get("profile_id") == profile_id:
                model.update(sub_dict(data[0], self.profile_ps.EDU_KEYS))

        self.send_json_success(
            data=self._make_json_data(route=route, model=model, new=new, constant=constant))

    @tornado.gen.coroutine
    def post_eduexp(self):
        profile_id = self._get_profile_id()
        model = objectdictify(self.params.model)

        if hasattr(model, "__status") and getattr(model, "__status") == 'x':
            verb = "delete"
        else:
            if model.description and len(model.description) > 1000:
                self.send_json_error(message=msg.PROFILE_OVERLENGTH % "教育描述")
                return
            verb = 'update' if model.id else 'create'

        result, res = yield getattr(
            self.profile_ps, verb + "_profile_education")(model, profile_id)

        if result:
            self.send_json_success()
        else:
            self.send_json_error()
    # Profile 编辑 -- eduexp 结束

    # Profile 编辑 -- projectexp 开始
    @tornado.gen.coroutine
    def get_projectexp(self):
        profile_id = self._get_profile_id()
        route = self.params.route

        scale_list = yield self.dictionary_ps.get_constants(
            parent_code=const.CONSTANT_PARENT_CODE.COMPANY_SCALE)
        constant = ObjectDict(scale_list=scale_list)

        model = {}
        new = False

        if not self.params.id:
            new = True

        else:
            result, data = yield self.profile_ps.get_profile_projectexp(
                projectexp_id=self.params.id)
            if result and data[0].get('profile_id') == profile_id:
                model.update(sub_dict(data[0], self.profile_ps.PROJECTEXP_KEYS))

        self.send_json_success(
            data=self._make_json_data(route=route, model=model, new=new,
                                      constant=constant))

    @tornado.gen.coroutine
    def post_projectexp(self):
        profile_id = self._get_profile_id()
        model = objectdictify(self.params.model)

        if hasattr(model, "__status") and getattr(model, "__status") == 'x':
            verb = "delete"
        else:
            if model.description and len(model.description) > 1000:
                self.send_json_error(message=msg.PROFILE_OVERLENGTH % "项目描述")
                return
            verb = 'update' if model.id else 'create'

        result, res = yield getattr(
            self.profile_ps, verb + "_profile_projectexp")(model, profile_id)

        if result:
            self.send_json_success()
        else:
            self.send_json_error()
    # Profile 编辑 -- projectexp 结束

    # Profile 编辑 -- prize 开始
    @tornado.gen.coroutine
    def get_prize(self):
        awards = self.current_user.profile.awards
        route = self.params.route
        model = [sub_dict(s, self.profile_ps.AWARDS_KEYS) for s in awards]
        self.send_json_success(data=self._make_json_data(route, model))

    @tornado.gen.coroutine
    def post_prize(self):
        profile_id = self._get_profile_id()
        model = objectdictify(self.params.model)  # =>List

        results = []
        for e in model:
            if hasattr(e, "__status") and getattr(e, "__status") == 'x':
                verb = "delete"
            else:
                verb = 'update' if e.id else 'create'
            result, res = yield getattr(
                self.profile_ps, verb + "_profile_awards")(e, profile_id)
            results.append(result)

        self._send_json_result(results, len(model))
    # Profile 编辑 -- prize 结束

    # Profile 编辑 -- link 开始
    @tornado.gen.coroutine
    def get_link(self):
        works = self.current_user.profile.works
        route = self.params.route
        new = not bool(works)
        if not new:
            model = sub_dict(works[0], self.profile_ps.WORKS_KEYS)
        else: model = {}

        self.send_json_success(
            data=self._make_json_data(route, model, new=new))

    @tornado.gen.coroutine
    def post_link(self):
        profile_id = self._get_profile_id()
        model = objectdictify(self.params.model)

        if model.id:
            verb = "update"
        else:
            verb = "create"

        result, _ = yield getattr(
            self.profile_ps, verb + "_profile_works")(model, profile_id)

        if result:
            self.send_json_success()
        else:
            self.send_json_error()
    # Profile 编辑 -- link 结束

    # Profile 编辑 -- jobpref 开始
    @tornado.gen.coroutine
    def get_jobpref(self):
        profile_id = self._get_profile_id()
        route = self.params.route

        worktype_list = yield self.dictionary_ps.get_constants(
            parent_code=const.CONSTANT_PARENT_CODE.WORK_INTENTION)
        salary_list = yield self.dictionary_ps.get_constants(
            parent_code=const.CONSTANT_PARENT_CODE.CURRENT_SALARY_MONTH)

        constant = ObjectDict()
        constant.worktype_list = worktype_list
        constant.salary_list = salary_list

        model = ObjectDict()
        new = False

        if not self.params.id:
            new = True
        else:
            result, intention = yield self.profile_ps.get_profile_intention(
                self.params.id)

            if result and intention and intention[0].get("profile_id", 0) == profile_id:
                intention = ObjectDict(intention[0])

                model.update(
                    sub_dict(intention, self.profile_ps.INTENTION_KEYS))

                positions = intention.positions
                if positions:
                    position_name = positions[0].get("position_name")
                    model.position_name = position_name

                cities = intention.cities
                if cities:
                    city_name = cities[0].get("city_name")
                    model.city_name = city_name
            else:
                self.send_json_error('cannot get intention')

        self.send_json_success(data=self._make_json_data(
            route=route, model=model, new=new,
            constant=constant))

    @tornado.gen.coroutine
    def post_jobpref(self):
        profile_id = self._get_profile_id()
        model = ObjectDict(self.params.model)
        verb = 'update' if model.id else 'create'
        result, _ = yield getattr(self.profile_ps, verb + "_profile_intention")(model, profile_id)

        if result:
            self.send_json_success()
        else:
            self.send_json_error()
    # Profile 编辑 -- jobpref 结束

    def _send_json_result(self, results, component_len):
        """json api 返回修改成功，失败，部分成功的"""
        success_results = [result for result in results if result is True]
        if len(success_results) == component_len:
            self.send_json_success()
        elif len(success_results):
            self.send_json_warning()
        else:
            self.send_json_error()
