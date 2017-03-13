# coding=utf-8

import tornado
import tornado.gen
from tornado.escape import json_decode, json_encode

from handler.base import BaseHandler

from util.common.decorator import handle_response, check_and_apply_profile
from util.common import ObjectDict
from util.tool.str_tool import mobile_validate
from util.tool.dict_tool import sub_dict, objectdictify
from util.tool.url_tool import make_url

import conf.common as const
import conf.message as msg
import conf.path as path


class ProfileHandler(BaseHandler):
    """ProfileHandler
    GET Profile 页面渲染
    POST 手动创建Profile -> 俗称老6步
    """

    @handle_response
    # @check_and_apply_profile
    @tornado.gen.coroutine
    def get(self):
        """ 查看个人 Profile
        如果有 GET 请求参数包含 pid,
        在 profile 页面吸顶显示申请按钮
        """
        # is_apply = self.params.get("apply", '0')

        # TODO (tangyiliang) use decorator
        # # 对雅诗兰黛无微不至的特别服务
        # is_skip = self.params.get("is_skip", '0')
        #
        # pid = self.params.get("pid", 0)
        # if not pid and self.get_cookie("dq_pid", 0):
        #     pid = int(self.get_cookie("dq_pid"))
        # if not is_apply and pid:
        #     is_apply = "1"

        # TODO (tangyiliang) use decorator
        # 获取不到 Profile 的情况下,跳转到新建 Profile 页面,
        # 雅诗兰黛的自定义职位,跳转到新六步
        # profile = yield self._prepare()
        # if not profile:
        #     no_profile_redirection(self, pid)
        #     return

        need_mobile_confirmation = 0
        # if is_apply and pid:
        #     if str(self.current_user.sysuser.mobile) != str(
        #         self.current_user.sysuser.username):
        #         need_mobile_confirmation = 1

        # profile_other 获取和处理
        # other_record = get_profile_other_by_profile_id(
        #     self.db, profile.get('profile').get('id'))
        # if other_record:
        #     other = json_decode(other_record.other)
        # else:
        #     other = {}
        # other = {}
        #
        # if other:
        #     other = sub_dict(other, pure_other_keys())

        other = {}
        self.params.profile=ObjectDict()
        profile_tpl = self.profile_ps.profile_to_tempalte(
            self.params.profile, other)

        self.render(
            template_name='profile/main.html',
            profile_json=profile_tpl)


    @tornado.gen.coroutine
    def post(self):
        has_profile, _ = yield self.profile_ps.has_profile(
            self.current_user.sysuser.id)
        if has_profile:
            self.send_json_error(message='profile existed')

        profile_data = self.request.body_arguments.get("profile", None)
        assert profile_data is not None
        profile = ObjectDict(json_decode(profile_data[0]))

        # 姓名必填
        if not profile.basicInfo or not profile.basicInfo.get('name', None):
            message = "".join([msg.PROFILE_REQUIRED_HINT_HEAD, u"姓名",
                               msg.PROFILE_REQUIRED_HINT_TAIL])
            self.render('weixin/profile/mobile.html', profile=profile,
                        message=message)
            return

        # 手机号必填
        if not profile.contacts or not profile.contacts.get('mobile', None):
            message = "".join([msg.PROFILE_REQUIRED_HINT_HEAD, u"手机号",
                               msg.PROFILE_REQUIRED_HINT_TAIL])
            self.render('weixin/profile/mobile.html', profile=profile,
                        message=message)
            return

        # 手机号格式验证
        ok = mobile_validate(profile.contacts.get('mobile', None))
        if not ok:
            message = "手机号码格式不正确"  # 手机号码格式不正确
            self.render('weixin/profile/mobile.html',
                        profile=profile, message=message)
            return

        # TODO
        # 更新 user_user 表的字段,
        # 这里使用 [] 可以让程序在需要时报错查看是否有漏洞导致需要的数据没有获取到
        # self._profile_service.update_user_user_fields(ObjectDict(
        #     mobile=profile.contacts['mobile'],
        #     name=profile.basicInfo['name'],
        #     email=profile.contacts['email'],
        #     headimg=None
        # ), self.current_user.sysuser.id)

        # PROFILE_PROFILE
        profile_id = None
        profile_ok = basic_info_ok = education_ok = workexp_ok = 0

        res_profile = yield self._profile_service.create_profile(
            self.current_user.sysuser.id)

        if res_profile[0]:
            profile_id = res_profile[1]
            profile_ok = 1
            # 初始化user_setting表，profile的公开度
            yield self.sysuser_service.post_user_setting(
                self.current_user.sysuser.id)
        else:
            self.LOG.error(
                "profile_profile creation failed. res:{}".format(
                    res_profile[1]))

        if profile_id:
            # BASIC INFO
            res_basic_info = yield self._profile_service.create_basic_info(
                profile, profile_id)
            if res_basic_info[0]:
                basic_info_ok = 1
            else:
                self.LOG.error(
                    "profile_basic creation failed. res:{}".format(
                        res_basic_info[1]))

            # EDUCATION
            education_res = yield self._profile_service.create_education(
                profile, profile_id)
            if education_res[0]:
                education_ok = 1
                self.LOG.debug(
                    "profile_education creation passed. New record num:{}"
                    .format(education_res[1]))
            else:
                self.LOG.error(
                    "profile_education creation failed. res:{}".format(
                        education_res[1]))

            # WORK EXP
            workexp_res = yield self._profile_service.create_workexp(
                profile, profile_id)
            if workexp_res[0]:
                workexp_ok = 1
                self.LOG.debug(
                    "profile_work_exp creation passed. New record num:{}"
                    .format(workexp_res[1]))
            else:
                self.LOG.error(
                    "profile_work_exp creation failed. res:{}".format(
                        workexp_res[1]))

        if profile_ok and basic_info_ok and education_ok and workexp_ok:
            is_apply = '1' if self.get_cookie('dq_pid') else '0'
            pid = self.get_cookie('dq_pid', None)

            data = ObjectDict(
                url=make_url(path.PROFILE, self.params, escape=['profile', 'abapply'], m='view',
                             apply=is_apply, pid=pid)
            )
            self.send_json_success(data)
        else:
            self.send_json_warning(message='profile created partially')


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
        component: "", // 模块名称
        componentData: { // 模块所需数据
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
    @tornado.gen.coroutine
    def get(self):
        # 根据 route 跳转到不同的子方法
        self.guarantee('route', 'component', 'componentData')
        yield getattr(self, "get_" + self.params.route)()

    @handle_response
    @tornado.gen.coroutine
    def post(self):
        # 根据 route 跳转到不同的子方法
        self.guarantee('route', 'component', 'componentData')
        yield getattr(self, "post_" + self.params.route)()


    #
    # @tornado.gen.coroutine
    # def get_manual(self):
    #     """
    #     手动创建 Profile
    #     先查看有无 pid, 然后根据职位判断:
    #     如果该职位是自定义职位,跳转到自定义简历页面填写
    #     否则,跳转到老六步
    #     """
    #     pid = self.params.pid or self.get_cookie('dq_pid', 0)
    #     if pid:
    #         pos_ser = positionService(self.db)
    #         position = pos_ser.get_position_info(pid)
    #         if position.app_cv_config_id > 0:
    #             user_id = self.current_user.sysuser.id
    #             sysuser_ser = sysuserService(self.db)
    #
    #             user = sysuser_ser.get_sysuser_by_id(user_id)
    #             user_info = ObjectDict(
    #                 email=user.email if user.email else "",
    #                 mobile=user.mobile if user.mobile else ""
    #             )
    #
    #             config = pos_ser.get_custom_template(position.app_cv_config_id)
    #             json_config = json_decode(config.field_value)
    #             self.render(
    #                 'weixin/application/app_cv_conf.html',
    #                 resume=json_encode(json_encode(user_info)) if user_info
    #                 else None,
    #                 cv_conf=json_encode(json_encode(json_config)))
    #             return
    #
    #     basicinfo = ObjectDict(
    #         name='',
    #         email=self.current_user.sysuser.email or '',
    #         mobile=self.current_user.sysuser.mobile or ''
    #     )
    #
    #     # 根据 params.pid 判断 JD 的职位 id
    #     # 判断是否需要跳过工作经历的填写
    #     jump_work_exp = 0
    #     if pid:
    #         position = positionDao.get_position_by_id(self, pid)
    #         # candidate_source = 0(社招)/1(校招)/2(定向招聘)
    #         if position and position.candidate_source == 1:
    #             jump_work_exp = position.candidate_source
    #
    #     self.render('neo_weixin/profile/new.html',
    #                 basicinfo=basicinfo,
    #                 degree_mapping=const.DICT_PROFILE_EDUCATION_DEGREE,
    #                 gender_mapping=const.DICT_PROFILE_GENDER,
    #                 total_steps=(5 if jump_work_exp else 6),
    #                 jump_work_exp=jump_work_exp)
    #

    #
    # @tornado.gen.coroutine
    # def post_custom_create(self):
    #     """
    #     自定义配置简历的post保存
    #     :return:
    #     """
    #     try:
    #         yield self._custom_create()
    #         p = dict(m='view', apply='1')
    #
    #         if self.current_user.company.id == const.CUSTOM_C_ID.EsteeLauder:
    #             pid = self.params.get("pid", 0)
    #             if not pid and self.get_cookie("dq_pid", 0):
    #                 pid = int(self.get_cookie("dq_pid"))
    #             if pid:
    #                 pos_ser = positionService(self.db)
    #                 position = pos_ser.get_position_info(pid)
    #                 if position.app_cv_config_id:
    #                     self.LOG.debug(u"雅诗兰黛特殊处理: 直接投递")
    #                     p.update(is_skip='1')
    #
    #         self.redirect(
    #             make_url(const.PROFILE_URL, self.params, **p))
    #
    #     except Exception as e:
    #         self.LOG.error(e)
    #         raise e
    #
    # @tornado.gen.coroutine
    # def _custom_create(self):
    #     """
    #     自定义配置简历的post保存
    #     """
    #     try:
    #         custom_cv = json_decode(self.get_argument("_cv", ""))
    #         if not custom_cv:
    #             raise Exception("get custom_cv failed")
    #
    #         # 更新 user_user 表的字段,
    #         self._profile_service.update_user_user_fields(ObjectDict(
    #             mobile=custom_cv.get('mobile'),
    #             name=custom_cv.get('name'),
    #             email=custom_cv.get('email')
    #             # 自定义字段中上传的头像不作为 user_user 的头像
    #             # headimg=custom_cv.get('picUrl')
    #         ), self.current_user.sysuser.id)
    #
    #         # PROFILE_PROFILE
    #         has_profile, profile = yield self._profile_service.has_profile(
    #             self.current_user.sysuser.id)
    #
    #         profile_id = profile.get("profile", {}).get("id", None)
    #
    #         if has_profile:
    #             old_basic = profile.get("basic")
    #             old_basic.update(custom_cv)
    #             yield self._profile_service.update_profile_basic(
    #                 profile_id, old_basic)
    #             yield (
    #                 self.
    #                 _profile_service.update_profile_embedded_info_from_cv(
    #                     profile_id, custom_cv))
    #
    #         else:
    #             source = 4 if self.PROJECT == const.PROJECT_BAGGING else 1
    #             res_profile = yield self._profile_service.create_profile(
    #                 self.current_user.sysuser.id,
    #                 source=source)
    #
    #             if res_profile[0]:
    #                 profile_id = res_profile[1]
    #
    #                 cv_profile_values = {
    #                     key: value for key, value in custom_cv.iteritems()
    #                     if key in cv_profile_keys_profile_basic()
    #                     }
    #
    #                 # BASIC INFO
    #                 res_basic_info = yield \
    #                     self._profile_service.create_profile_basic_from_cv(
    #                         cv_profile_values, profile_id)
    #                 if res_basic_info[0]:
    #                     self.LOG.debug(
    #                         "profile_basic creation passed. Got basic info "
    #                         "id:{}".format(res_basic_info[1]))
    #                 else:
    #                     self.LOG.error(
    #                         "profile_basic creation failed. res:{}"
    #                         .format(res_basic_info[1]))
    #
    #                 # 初始化user_setting表，profile的公开度
    #                 yield self.sysuser_service.post_user_setting(
    #                     self.current_user.sysuser.id)
    #
    #                 yield (
    #                     self.
    #                     _profile_service.update_profile_embedded_info_from_cv(
    #                         profile_id, custom_cv))
    #             else:
    #                 self.LOG.error(
    #                     "profile_profile creation failed. res:{}".format(
    #                         res_profile[1]))
    #
    #         if profile_id:
    #             # profile = ObjectDict()
    #             # basicInfo = ObjectDict()
    #
    #             # const.CUSTOM_FIELD_NAME_TO_PROFILE_FIELD
    #             # 为自定义字段到 profile 字段的对应
    #
    #             # 如果 value 为 "",表明没有对应的 profile 字段,
    #             # 应该存入 profile_others
    #             # 因为 profile 对应字段都是属于 basic 的,所以都加入 basicInfo 中
    #             # 这样可以做到和老六步兼容
    #             #  *const.CUSTOM_FIELD_NAME_TO_PROFILE_FIELD 需要微信后端自行维护
    #
    #             # 自定义简历模版提交的 picUrl 作为 IDPhoto 使用
    #             if custom_cv.get('picUrl'):
    #                 custom_cv['IDPhoto'] = custom_cv.get('picUrl')
    #
    #             cv_pure_custom = {
    #                 key: value for key, value in custom_cv.iteritems()
    #                 if key in cv_pure_custom_keys()
    #             }
    #
    #             profile_dao.update_profile_other_by_profile_id(
    #                 self.db, profile_id, cv_pure_custom)
    #
    #     except Exception as e:
    #         self.LOG.error(e)
    #         raise e

    ##########################################################################
    # profile 编辑
    ##########################################################################
    # def _get_to_field(self):
    #     ret = self.params.get('to', None)
    #     if not ret or ret not in self._EDITABLE_COMPONENT:
    #         return None
    #     return ret

    def _get_profile_id(self):
        """"""
        try:
            profile_id = self.current_user.profile.id
        except AttributeError as e:
            self.logger.error(e)
            self.logger.error('Forget to use @check_and_apply_profile?')
            raise
        else:
            return profile_id

    def _make_json_data(self, component=None, component_data=None,
                        constant=None, new=False):
        try:
            # TODO (yiliang) to check more
            assert component in self.profile_ps.FE_ROUTES.keys()
        except:
            raise ValueError('invalid component')

        data = ObjectDict(
            component=component,
            component_data=component_data,
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
        else: pass

        component = self.params.component

        if self_intro:
            component_data = sub_dict(profile_basic[0], 'self_introduction')
        else:
            component_data = sub_dict(profile_basic[0],
                                      self.profile_ps.BASIC_KEYS)

        self.send_json_success(
            data=self._make_json_data(component, component_data))

    @tornado.gen.coroutine
    def post_basic(self, self_intro=False):
        profile_id = yield self._get_profile_id()
        component_data = ObjectDict(json_decode(self.params.data))

        if component_data:
            basic = ObjectDict()
            if self_intro:
                basic.update(
                    self_introduction=component_data.self_introduction)
            else:
                basic.update(
                    sub_dict(component_data, self.profile_ps.BASIC_KEYS))
                basic.pop('self_introduction')

                if basic.city_name == "未知":
                    basic.pop('city_name')

            result, data = yield self.profile_ps.update_profile_basic(
                profile_id, basic)

            if result:
                self.send_json_success()
            else:
                self.send_json_error()
        else:
            self.send_json_error(message='no component_data')

    @tornado.gen.coroutine
    def get_description(self):
        yield self.get_edit_basic(self_intro=True)

    @tornado.gen.coroutine
    def post_description(self):
        yield self.post_edit_basic(self_intro=True)

    # Profile 编辑 -- basic & self-introduction 结束

    # Profile 编辑 -- language 开始
    @tornado.gen.coroutine
    def get_language(self):
        profile_id = yield self._get_profile_id()
        result, languages = yield self.profile_ps.get_profile_language(
            profile_id)
        if not result:
            raise ValueError('cannot get language')
        else:
            pass
        component = self.params.component

        component_data = []
        for l in languages:
            e = sub_dict(l, self.profile_ps.LANGUAGE_KEYS)
            e.update(language=e.name)
            del e['name']
            component_data.append(e)

        self.send_json_success(
            data=self._make_json_data(component, component_data))

    @tornado.gen.coroutine
    def post_language(self):
        profile_id = yield self._get_profile_id()
        component_data = objectdictify(self.params.data)

        results = []
        for e in component_data:
            if hasattr(e, "__status") and getattr(e, "__status") == 'x':
                verb = "delete"
            else:
                verb = 'update' if e.id else 'create'

            result, res = yield getattr(
                self.profile_ps, verb + "_profile_language")(e, profile_id)
            results.append(result)

        self._send_json_result(results, len(component_data))

    # Profile 编辑 -- language 结束

    # Profile 编辑 -- skill 开始
    @tornado.gen.coroutine
    def get_skill(self):
        profile_id = yield self._get_profile_id()
        result, skills = yield self._profile_service.get_profile_skill(
            profile_id)
        if not result:
            raise ValueError('cannot get skills')
        else: pass

        component = self.params.component
        component_data = []
        for s in skills:
            s = sub_dict(s, self.profile_ps.SKILL_KEYS)
            component_data.append(s)

        self.send_json_success(
            data=self._make_json_data(component, component_data))

    @tornado.gen.coroutine
    def post_skill(self):
        profile_id = yield self._get_profile_id()
        component_data = objectdictify(json_decode(self.params.data))

        results = []
        for e in component_data:
            if hasattr(e, "__status") and getattr(e, "__status") == 'x':
                verb = "delete"
            else:
                verb = 'update' if e.id else 'create'

            result, res = yield getattr(
                self.profile_ps, verb + "_profile_skill")(e, profile_id)
            results.append(result)

        self._send_json_result(results, len(component_data))

    # Profile 编辑 -- skill 结束

    # Profile 编辑 -- cert 开始
    @tornado.gen.coroutine
    def get_cert(self):
        profile_id = yield self._get_profile_id()
        result, certs = yield self.profile_ps.get_profile_cert(
            profile_id)
        if not result:
            raise ValueError('cannot get certs')

        component = self.params.component
        if result:
            component_data = []
            for s in certs:
                s = sub_dict(s, self._CERT_KEYS)
                component_data.append(s)
        else:
            component_data = None

        self.send_json_success(
            data=self._make_json_data(component, component_data))

    @tornado.gen.coroutine
    def post_cert(self):
        profile_id = yield self._get_profile_id()
        component_data = objectdictify(json_decode(self.params.data))

        results = []
        for e in component_data:
            if hasattr(e, "__status") and getattr(e, "__status") == 'x':
                verb = "delete"
            else:
                verb = 'update' if e.id else 'create'

            result, res = yield getattr(
                self.profile_ps, verb + "_profile_cert")(e, profile_id)
            results.append(result)

        self._send_json_result(results, len(component_data))

    # Profile 编辑 -- cert 结束

    # Profile 编辑 -- jobexp 开始
    @tornado.gen.coroutine
    def get_jobexp(self):
        profile_id = yield self._get_profile_id()
        component = self._get_to_field()

        scale_list = yield self.dictionary_ps.get_constants(
            parent_code=const.CONSTANT_PARENT_CODE.COMPANY_SCALE)
        constant = ObjectDict(scale_list=scale_list)

        component_data = {}
        new = False

        if not self.params.id:
            new = True

        else:
            workexp = yield self.profile_ps.get_profile_workexp(
                workexp_id=self.params.id)
            workexp = workexp[0]

            if workexp and profile_id == workexp.profile_id:
                component_data.update(
                    sub_dict(workexp, self.profile_ps.WORKEXP_KEYS))

        self.send_json_success(
            data=self._make_json_data(
                component=component,
                component_data=component_data,
                new=new,
                constant=constant))

    @tornado.gen.coroutine
    def post_jobexp(self):
        profile_id = yield self._get_profile_id()
        component_data = ObjectDict(json_decode(self.params.data))
        record = component_data

        if hasattr(record, "__status") and getattr(record, "__status") == 'x':
            verb = "delete"
        else:
            verb = 'update' if record.id else 'create'

        result, res = yield getattr(
            self.profile_ps, verb + "_profile_workexp")(
            record, profile_id)

        if result:
            self.send_json_success()
        else:
            self.send_json_error()

    @tornado.gen.coroutine
    def post_jobexp_company(self):
        profile_id = yield self._get_profile_id()
        component_data = ObjectDict(json_decode(self.params.data))
        record = ObjectDict(component_data)

        # 通过名称查询企业是否已经存在
        name = record.name
        result, res = yield self.company_ps.get_cp_for_sug_wechat(name)

        if result:
            self.send_json_error(message='company name existed')
            return
        else:
            result, res = yield self.company_ps.create_company_on_wechat(
                record)
            if result:
                self.send_json_success(message='company created')
            else:
                self.send_json_error(message='company creation error')
    # Profile 编辑 -- jobexp 结束

    # Profile 编辑 -- eduexp 开始
    @tornado.gen.coroutine
    def get_eduexp(self):
        profile_id = yield self._get_profile_id()
        component = self.params.component

        degree_list = yield self.dictionary_ps.get_constants(
            parent_code=const.CONSTANT_PARENT_CODE.DEGREE_USER)
        constant = {'degree_list': degree_list}

        component_data = {}
        new = False

        if not self.params.id:
            new = True

        else:
            education = yield self.profile_ps.get_profile_education(
                education_id=self.params.id)
            education = education[0]

            if education and profile_id == education.get("profile_id"):
                component_data.update(sub_dict(
                    education, self.profile_ps.EDU_KEYS))

        self.send_json_success(
            data=self._make_json_data(
                component=component,
                component_data=component_data,
                new=new,
                constant=constant))

    @tornado.gen.coroutine
    def post_eduexp(self):
        profile_id = yield self._get_profile_id()
        component_data = ObjectDict(json_decode(self.params.data))
        record = component_data

        if hasattr(record, "__status") and getattr(record, "__status") == 'x':
            verb = "delete"
        else:
            verb = 'update' if record.id else 'create'

        result, res = yield getattr(
            self._profile_service, verb + "_profile_education")(
            record, profile_id)

        if result:
            self.send_json_success()
        else:
            self.send_json_error()
    # Profile 编辑 -- eduexp 结束

    # Profile 编辑 -- projectexp 开始
    @tornado.gen.coroutine
    def get_projectexp(self):
        profile_id = yield self._get_profile_id()
        component = self.params.component

        scale_list = yield self.dictionary_ps.get_constants(
            parent_code=const.CONSTANT_PARENT_CODE.COMPANY_SCALE)
        constant = ObjectDict(scale_list=scale_list)

        component_data = {}
        new = False

        if not self.params.id:
            new = True

        else:
            projectexp = yield self.profile_ps.get_profile_projectexp(
                projectexp_id=self.params.id)
            projectexp = projectexp[0]

            if projectexp and profile_id == projectexp.get("profile_id"):
                component_data.update(sub_dict(
                    projectexp, self.profile_ps.PROJECTEXP_KEYS))

        self.send_json_success(
            data=self._make_json_data(
                component=component,
                component_data=component_data,
                new=new,
                constant=constant))

    @tornado.gen.coroutine
    def post_edit_projectexp(self):
        profile_id = yield self._get_profile_id()
        component_data = ObjectDict(json_decode(self.params.data))
        record = component_data
        if hasattr(record, "__status") and getattr(record, "__status") == 'x':
            verb = "delete"
        else:
            verb = 'update' if record.id else 'create'

        result, res = yield getattr(
            self._profile_service, verb + "_profile_projectexp")(
            record, profile_id)

        if result:
            self.send_json_success()
        else:
            self.send_json_error()

    # Profile 编辑 -- projectexp 结束

    # Profile 编辑 -- prize 开始
    @tornado.gen.coroutine
    def get_prize(self):
        profile_id = yield self._get_profile_id()
        component = self.params.component

        result, awards = yield self.profile_ps.get_profile_awards(profile_id)

        component_data = []
        if result:
            for award in awards:
                component_data.append(sub_dict(
                    award, self.profile_ps.AWARDS_KEYS))
        else:
            component_data = None

        self.send_json_success(
            data=self._make_json_data(component, component_data))

    @tornado.gen.coroutine
    def post_prize(self):
        profile_id = yield self._get_profile_id()
        component_data = objectdictify(json_decode(self.params.data))  # =>List

        results = []
        for e in component_data:
            if hasattr(e, "__status") and getattr(e, "__status") == 'x':
                verb = "delete"
            else:
                verb = 'update' if e.id else 'create'

            result, res = yield getattr(
                self._profile_service, verb + "_profile_awards")(e, profile_id)

            results.append(result)

        self._send_json_result(results, len(component_data))
    # Profile 编辑 -- prize 结束

    # Profile 编辑 -- link 开始
    @tornado.gen.coroutine
    def get_link(self):
        profile_id = yield self._get_profile_id()
        component = self.params.component

        new = False
        component_data = {}

        if not self.params.id:
            new = True
        else:
            result, works = yield self._profile_service.get_profile_works(
                self.params.id)

            if result and works and works[0].profile_id == profile_id:
                component_data.update(
                    sub_dict(works[0], self.profile_ps.WORKS_KEYS))
            else:
                self.send_json_error('cannot get works')

        self.send_json_success(
            data=self._make_json_data(component, component_data, new=new))

    @tornado.gen.coroutine
    def post_link(self):
        profile_id = yield self._get_profile_id()
        component_data = ObjectDict(json_encode(self.params.data))

        record = component_data
        if record.id:
            verb = "update"
        else:
            verb = "create"

        result, _ = yield getattr(
            self._profile_service, verb + "_profile_works")(record, profile_id)

        if result:
            self.send_json_success()
        else:
            self.send_json_error()
    # Profile 编辑 -- link 结束

    # Profile 编辑 -- jobpref 开始
    @tornado.gen.coroutine
    def get_jobpref(self):
        profile_id = yield self._get_profile_id()
        component = self.params.component

        worktype_list = yield self.dictionary_ps.get_constants(
            parent_code=const.CONSTANT_PARENT_CODE.WORK_INTENTION)
        salary_list = yield self.dictionary_ps.get_constants(
            parent_code=const.CONSTANT_PARENT_CODE.CURRENT_SALARY_MONTH)

        constant = ObjectDict()
        constant.worktype_list = worktype_list
        constant.salary_list = salary_list

        component_data = ObjectDict(),
        new = False

        if not self.params.id:
            new = True
        else:
            result, intention = yield self.profile_ps.get_profile_intention(
                self.params.id)

            if result and intention and intention[0].profile_id == profile_id:
                intention = ObjectDict(intention[0])

                component_data.update(
                    sub_dict(intention, self.profile_ps.INTENTION_KEYS))

                positions = intention.positions
                if positions:
                    position_name = positions[0].get("position_name")
                    component_data.position_name = position_name

                cities = intention.cities
                if cities:
                    city_name = cities[0].get("city_name")
                    component_data.city_name = city_name
            else:
                self.send_json_error('cannot get intention')

        self.send_json_success(data=self._make_json_data(
            component=component, component_data=component_data, new=new,
            constant=constant))

    @tornado.gen.coroutine
    def post_jobpref(self):
        profile_id = yield self._get_profile_id()
        component_data = json_decode(self.params.data)
        record = ObjectDict(component_data)

        verb = 'update' if record.id else 'create'

        result, _ = yield getattr(
            self._profile_service, verb + "_profile_intention")(
            record, profile_id)

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
