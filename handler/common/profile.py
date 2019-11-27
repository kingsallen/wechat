# coding=utf-8

import json

import tornado.gen
from tornado.escape import json_decode

import conf.common as const
import conf.message as msg
import conf.path as path
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, check_and_apply_profile, \
    authenticated
from util.tool.dict_tool import sub_dict, objectdictify
from util.tool.file_tool import filetype
from util.tool.str_tool import mobile_validate
from util.tool.json_tool import json_dumps
from conf.locale_dict import CITY, CITY_REVERSE, INDUSTRY, INDUSTRY_REVERSE
from util.common.exception import InfraOperationError
import operator


class ProfileNewHandler(BaseHandler):

    @handle_response
    @authenticated
    @tornado.gen.coroutine
    def get(self):
        """初始化新建 profile 页面"""
        display_locale = self.get_current_locale()
        pid = self.params.pid
        position = yield self.position_ps.get_position(pid)
        if position.candidate_source == "common_graduate":
            is_graduate = True
        else:
            is_graduate = False
        # yield from ps
        data = yield dict(
            degreeList=self.dictionary_ps.get_degrees(self.locale, no_key=True),  # 内推和这里需要的结构不同，用no_key做区分
            countryCodeList=self.dictionary_ps.get_sms_country_codes(display_locale))

        # update other initial values
        data.update(
            email='', mobile='', country_code='86', mobileeditable=True, is_graduate=is_graduate)

        data = ObjectDict(data)
        sysuser = self.current_user.sysuser
        if sysuser:
            data.email = sysuser.email
            data.mobile = str(sysuser.mobile) if sysuser.mobile else ''
            data.country_code = sysuser.country_code
            data.mobileeditable = not sysuser.mobileverified

        self.send_json_success(data=data)

    @handle_response
    @authenticated
    @tornado.gen.coroutine
    def post(self):

        has_profile, profile = yield self.profile_ps.has_profile(self.current_user.sysuser.id)
        if has_profile:
            message = "简历已存在，请返回个人档案页刷新"
            self.send_json_error(message=message)
            return

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

        phone_number = profile.contacts.get('mobile')
        country_code = profile.contacts.get('country_code')

        yield self.user_ps.update_user(
            self.current_user.sysuser.id,
            name=profile.basicInfo['name'],
            email=profile.contacts['email'],
            mobile="{}-{}".format(country_code, phone_number)
        )

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
            self.logger.debug("profile_profile created with id: %s" % profile_id)
            self._log_customs.update(new_profile=const.YES)
        else:
            self.logger.error("profile_profile creation failed. res:{}".format(data))
            self.send_json_error()
            return

        self.logger.debug("[profile post]profile:{}".format(profile))

        result, data = yield self.profile_ps.create_profile_basic(profile, profile_id)
        if result:
            basic_info_ok = True
            self.logger.debug("profile_basic created, id: %s" % data)
        else:
            self.logger.error("profile_basic creation failed. res: %s" % data)

        self.logger.debug("[profile post]create_profile_basic result:{}".format(result))
        self.logger.debug("[profile post]create_profile_basic data:{}".format(data))

        for edu in profile.education:
            self.logger.debug("[profile post]profile.education edu:{}".format(edu))
            result, data = yield self.profile_ps.create_profile_education(ObjectDict(edu), profile_id)
            if result:
                self.logger.debug("profile_education creation passed. New record num: %s" % data)
            else:
                education_ok = False
                self.logger.error("profile_education creation failed. res: %s" % data)
                break

        self.logger.debug("[profile post]create_profile_education result:{}".format(result))
        self.logger.debug("[profile post]create_profile_education data:{}".format(data))

        for wxp in profile.workexp:
            self.logger.debug("[profile post]profile.workexp wxp:{}".format(wxp))
            result, data = yield self.profile_ps.create_profile_workexp(ObjectDict(wxp), profile_id)
            if result:
                self.logger.debug("profile_work_exp creation passed. New record num: %s" % data)
            else:
                workexp_ok = False
                self.logger.error("profile_work_exp creation failed. res: %s" % data)
                break

        self.logger.debug("[profile post]create_profile_workexp result:{}".format(result))
        self.logger.debug("[profile post]create_profile_workexp data:{}".format(data))

        # 只有全部 ok 后才可以跳转
        if profile_ok and basic_info_ok and education_ok and workexp_ok:
            dqpid = self.get_cookie('dqpid')
            self.logger.debug('dqpid: %s' % dqpid)
            recom = ''
            if 'recom' in self.json_args:
                recom = self.json_args.recom
            p = dict()
            if recom:
                p.update(recom=recom)
            if dqpid:
                next_url = self.make_url(path.PROFILE_PREVIEW, self.params, pid=str(dqpid), **p)
            else:
                next_url = self.make_url(path.PROFILE_VIEW, self.params, **p)
            self.logger.debug('next_url: %s' % next_url)
            self.clear_cookie(name='dqpid')
            self.send_json_success(data=ObjectDict(next_url=next_url))
        else:
            self.send_json_warning(message='profile created partially')


class APIProfileHandler(BaseHandler):

    @handle_response
    @tornado.gen.coroutine
    def get(self):
        user_id = self.current_user.sysuser.id if self.current_user.sysuser else 0
        if not user_id:
            self.send_json_error()
        else:
            result, profile = yield self.profile_ps.has_profile(user_id)
            if result:
                self.send_json_success(data=profile)


class APIProfileCompletenessHandler(BaseHandler):

    @handle_response
    @tornado.gen.coroutine
    def get(self):
        user_id = self.current_user.sysuser.id if self.current_user.sysuser else 0
        if not user_id:
            self.send_json_error()
        else:
            completeness = yield self.profile_ps.get_profile_completeness(user_id, timeout=3)
            if completeness:
                self.send_json_success(data=completeness)


class ProfilePreviewHandler(BaseHandler):

    @handle_response
    @check_and_apply_profile
    @authenticated
    @tornado.gen.coroutine
    def get(self):

        pid = self.params.pid

        if not pid or not pid.isdigit():
            url = self.make_url(path.PROFILE_VIEW, self.params)
            self.redirect(url)
            return

        profile_tpl = yield self.profile_ps.profile_to_tempalte(
            self.current_user.profile, self.locale)



        # -8<---8<---8<---8<---8<---8<---8<---8<---8<---8<---8<---8<---8<---
        # 只有存在 is_skip 且值为 '1' 时才跳过 preview
        try:
            is_skip = int(self.params.is_skip) == const.YES
        except Exception:
            is_skip = False
        # -8<---8<---8<---8<---8<---8<---8<---8<---8<---8<---8<---8<---8<---

        other_key_name_mapping = yield self.profile_ps.get_others_key_name_mapping(company_id=self.current_user.company.id, locale=self.locale)

        no_name = not bool(self.current_user.sysuser.name)
        need_mobile_validate = not bool(self.current_user.sysuser.mobileverified)

        current_mobile = ''
        if self.current_user.sysuser.mobile:
            current_mobile = str(self.current_user.sysuser.mobile)

        tparams = {
            'profile':                profile_tpl,
            'other_key_name_mapping': other_key_name_mapping,
            'pid':                    pid,
            'is_skip':                is_skip,
            'need_mobile_validate':   need_mobile_validate,
            'no_name':                no_name,
            'country_code':           self.current_user.sysuser.country_code,
            'current_mobile':         current_mobile,
        }

        self.render_page(template_name='profile/preview.html',
                         data=tparams,
                         meta_title=const.PROFILE_PREVIEW)


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
            redirect_url = self.make_url(path=path.PROFILE_VIEW, params=self.params)
            self.redirect(redirect_url)
            return

        profile_tpl = yield self.profile_ps.profile_to_tempalte(profile, self.locale)

        other_key_name_mapping = yield self.profile_ps.get_others_key_name_mapping(company_id=self.current_user.company.id, locale=self.locale)

        # 游客页不应该显示 other信息，求职意愿
        profile_tpl.other = ObjectDict()
        profile_tpl.job_apply = ObjectDict()

        tparams = {
            "other_key_name_mapping": other_key_name_mapping,
            "profile": profile_tpl,
            "is_self": False,
        }

        self.params.share = self._share(uuid, profile_tpl)
        self.render_page(template_name='profile/preview.html', data=tparams, meta_title=const.PROFIEL_VIEW)

    def _share(self, uuid, profile_tpl):
        default = ObjectDict({
            'cover': self.share_url(profile_tpl.avatar_url),
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
            self.current_user.profile, self.locale)

        other_key_name_mapping = yield self.profile_ps.get_others_key_name_mapping(company_id=self.current_user.company.id, select_all=True, locale=self.locale)

        self.params.share = self._share(self.current_user.profile.profile.get("uuid"), profile_tpl)
        self.render_page(
            template_name='profile/main.html',
            data=ObjectDict(profile=profile_tpl, other_key_name_mapping=other_key_name_mapping))

    def _share(self, uuid, profile_tpl):
        default = ObjectDict({
            'cover': self.share_url(profile_tpl.avatar_url),
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
        if not self.params.pid or not self.params.pid.isdigit():
            self.write_error(404)
            return

        pid = int(self.params.pid)
        position = yield self.position_ps.get_position(pid, display_locale=self.get_current_locale())

        if not position.app_cv_config_id:
            self.write_error(404)
            return

        has_profile, profile = yield self.profile_ps.has_profile(
            self.current_user.sysuser.id)
        custom_tpl = yield self.profile_ps.get_custom_tpl_all()

        if has_profile:
            resume_dict = yield self.application_ps._generate_resume_cv(profile, custom_tpl)
            if resume_dict.id_card_back:
                resume_dict.id_card_back = ""
            if resume_dict.id_card_front:
                resume_dict.id_card_front = ""
        else:
            # 如果没有仟寻profile，对于已经验证手机号的用户，自定义模板需要默认填上验证手机号，即user_user的username字段
            resume_dict = ObjectDict({'mobile': str(self.current_user.sysuser.mobile) if self.current_user.sysuser.mobile else ''})

        json_config = yield self.application_ps.get_hr_app_cv_conf(
            position.app_cv_config_id, self.locale)
        cv_conf = json.loads(json_config.field_value)
        idcards = []
        for conf in cv_conf:
            idcard = {}
            for field in conf.get("fields"):
                if field.get("field_name") == "id_card":  # 如果有身份证组件，组件下的子字段的required需根据身份证组件做修改
                    idcard = {"id": field.get('id'), "required": field.get('required')}
                    break
            idcards.append(idcard) #如果idcard是{}空，也追加进来

        idcard_oms = yield self.company_ps.check_oms_switch_status(
            self.current_user.company.id,
            "身份证识别"
        )
        if idcard_oms.status != const.API_SUCCESS:
            raise InfraOperationError(idcard_oms.message)

        cv_fields = []
        config = []
        if idcard_oms.data.get('valid'):
            for i in range(0, len(cv_conf)):
                if idcards[i]:
                    for field in cv_conf[i].get("fields"):
                        field["order"] = 2
                        if field.get("field_name") == "name": #name固定是必填字段
                            field["required"] = 0
                            field["order"] = 1
                        if field.get("field_name") in ["id_card", "gender", "birth", "idnumber", "id_card_front", "id_card_back", "id_card_addr"]:
                            field["required"] = idcards[i].get("required")
                            field["order"] = 1
                        if field.get("field_name") in ["name", "idnumber", "gender", "birth", "id_card_addr"]:
                            field["parent_id"] = 0
                    cv_conf[i]["fields"] =  sorted(cv_conf[i].get("fields"), key=operator.itemgetter('order'))
            config = cv_conf
        else:  # 如果oms关闭，去掉身份证照片
            for i in range(0, len(cv_conf)):
                if idcards[i]:
                    for field in cv_conf[i].get("fields"):
                        field["order"] = 2
                        if field.get("field_name") == "name":  # name固定是必填字段
                            field["required"] = 0
                            field["parent_id"] = 0
                            field["order"] = 1
                        if field.get("field_name") in ["idnumber", "gender", "birth", "id_card_addr"]:
                            field["required"] = idcards[i].get("required")
                            field["parent_id"] = 0
                            field["order"] = 1

                        if field.get("field_name") in ["id_card", "id_card_front", "id_card_back"]:
                            continue
                        cv_fields.append(field)
                    cv_fields = sorted(cv_fields, key=operator.itemgetter('order'))
                    config.append({"fields": cv_fields, "title": cv_conf[i].get("title")})
                else:
                    config.append(cv_conf[i])

        self.render_page(
            template_name='profile/custom.html',
            data=dict(resume=resume_dict,
                      has_profile=has_profile,
                      config=config))


class ProfileAPICustomCVHandler(BaseHandler):

    @handle_response
    @authenticated
    @tornado.gen.coroutine
    def post(self):

        if 'custom_cv' not in self.json_args:
            raise ValueError("Failed to get custom_cv")
        if 'pid' not in self.json_args:
            raise ValueError('Failed to get pid')

        recom = ''
        if 'recom' in self.json_args:
            recom = self.json_args.recom

        custom_cv = self.json_args.custom_cv
        pid = self.json_args.pid

        self.logger.debug("custom_cv: %s" % custom_cv)

        yield self._save_custom_cv(custom_cv)

        p = dict(is_skip='1' if self.current_user.company.id in self.customize_ps._DIRECT_APPLY else '0',
                 pid=pid)
        if recom:
            p.update(recom=recom)

        self.send_json_success(data={
            'next_url': self.make_url(path.PROFILE_PREVIEW, self.params, **p)
        })

    @tornado.gen.coroutine
    def _save_custom_cv(self, custom_cv):

        # --8<-- 初始化 --8<-----8<-----8<-----8<-----8<-----8<-----8<-----8<--
        profile_id = None
        custom_cv_tpls = yield self.profile_ps.get_custom_tpl_all()

        custom_cv_user_user = self.profile_ps.convert_customcv(custom_cv, custom_cv_tpls, target='user_user')
        custom_cv_profile_basic = self.profile_ps.convert_customcv(custom_cv, custom_cv_tpls, target='profile_basic')
        custom_cv_other_raw = self.profile_ps.convert_customcv(custom_cv, custom_cv_tpls, target='other')

        self.logger.debug("custom_cv_user_user: %s" % custom_cv_user_user)
        self.logger.debug("custom_cv_profile_basic: %s" % custom_cv_profile_basic)
        self.logger.debug("custom_cv_other_raw: %s" % custom_cv_other_raw)

        # --8<-- 更新 user_user --8<-----8<-----8<-----8<-----8<-----8<------
        if custom_cv_user_user:
            result = yield self.user_ps.update_user(
                self.current_user.sysuser.id,
                **custom_cv_user_user)

            self.logger.debug("update_user result: %s" % result)

        # --8<-- 检查profile --8<-----8<-----8<-----8<-----8<-----8<-----8<---
        has_profile, profile = yield self.profile_ps.has_profile(
            self.current_user.sysuser.id)
        if has_profile:
            profile_id = profile.get("profile", {}).get("id")
        else:
            # 还不存在 profile， 创建 profile
            # 进入自定义简历创建 profile 逻辑的话，来源必定是企业号（我要投递）
            result, data = yield self.profile_ps.create_profile(
                self.current_user.sysuser.id,
                source=const.PROFILE_SOURCE_PLATFORM_APPLY)

            # 创建 profile 成功
            if not result:
                raise RuntimeError('profile creation error')

            profile_id = data

            self._log_customs.update(new_profile=const.YES)

        # 创建完 profile 后再次获取 profile
        has_profile, profile = yield self.profile_ps.has_profile(
            self.current_user.sysuser.id)

        if custom_cv_profile_basic:
            # 已经有 profile，
            basic = profile.get("basic")

            result, data = yield self.profile_ps.get_profile_basic(profile_id = profile_id)

            has_no_basic =  not result and data.status == 90010

            basic.update(custom_cv_profile_basic)
            self.logger.debug("updated basic: %s" % basic)

            if has_no_basic:
                basic.update({'profile_id': profile_id})
                yield self.profile_ps.create_profile_basic(
                    basic, profile_id, mode='c')
            else:
                yield self.profile_ps.update_profile_basic(profile_id, basic)

        # 更新多条 education, workexp, projectexp, language, awards,
        # 更新单条 intention, works
        yield self.profile_ps.update_profile_embedded_info_from_cv(
            profile_id, profile, custom_cv)

        # 更新 other
        if custom_cv_other_raw:
            yield self.update_profile_other(profile_id, custom_cv_other_raw)

    @staticmethod
    def _preprocess_custom_cv(custom_cv_other_raw):
        """对于纯 profile 字段的预处理
        可以在此加入公司自定义逻辑"""
        ret = json.dumps(custom_cv_other_raw)
        ret = json.loads(ret)

        # 前端 rocketmajor_value 保存应该入库的 rocketmajor 字段内容
        if ret.get('rocketmajor_value'):
            ret['rocketmajor'] = ret.get('rocketmajor_value')
            del ret['rocketmajor_value']

        # 确保保存正确的 schooljob 和 internship
        def _filter_elements_in(name):
            new_list = []
            for e in ret.get(name):
                if e.get('__status') and not e.get('__status') == 'x':
                    e.pop('__status', None)
                    until_now_key = name + 'end_until_now'
                    until_now = int(e.get(until_now_key, '0'))
                    if until_now:
                        e['end_date'] = None
                    new_list.append(e)
            return new_list

        if ret.get('internship'):
            ret['internship'] = _filter_elements_in('internship')

        if ret.get('schooljob'):
            ret['schooljob'] = _filter_elements_in('schooljob')

        return ret

    @tornado.gen.coroutine
    def update_profile_other(self, profile_id, custom_cv_other_raw):
        """智能地更新 profile_other 内容"""
        custom_cv_ready = self._preprocess_custom_cv(custom_cv_other_raw)

        other_string = json_dumps(custom_cv_ready)
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
        # 神策埋点
        self._add_sensor_track()
        self._log_customs.update(update_profile=const.YES,
                                 section=self.params.route)

    def _add_sensor_track(self):
        if self.params.promote == const.PROMOTE:
            origin = const.SA_ORIGIN_PROMOTE
        else:
            origin = const.SA_ORIGIN_PLATFORM
        self.track("wxUpsertProfile", properties={"origin": origin})

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
        route = self.params.route

        if not result:
            model = ObjectDict()
        else:
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
                model.pop('self_introduction', None)

                if model.city_name == "未知" or model.city_name is None:
                    model.pop('city_name', None)

            has_basic = yield self.profile_ps.has_profile_basic(profile_id)
            if has_basic:
                result, data = yield self.profile_ps.update_profile_basic(
                    profile_id, model)
            else:
                model.update(profile_id=profile_id)
                result, data = yield self.profile_ps.create_profile_basic(
                    model, profile_id, mode='c')

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
                for symbol in """，,、:：;；‘’'“”""''""":
                    if symbol in e.get("language"):
                        self.send_json_error(message=self.locale.translate('profile_check_char'))
                        return
                if self.get_bit_count(e.get("language"), 40) > 40:
                    self.send_json_error(message=self.locale.translate('profile_check_length'))
                    return
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

    def get_bit_count(self, str_value, max_length):
        '包含汉字的占2个位，其他一个占一个'
        bit_count = 0
        for c in str_value:
            if bit_count > max_length:
                break
            if '\u4e00' <= c <= '\u9fa5':
                bit_count += 2
            else:
                bit_count += 1
        return bit_count

    @tornado.gen.coroutine
    def post_skill(self):
        profile_id = self._get_profile_id()
        model = objectdictify(self.params.model)

        results = []
        for e in model:
            if hasattr(e, "__status") and getattr(e, "__status") == 'x':
                verb = "delete"
            else:
                for symbol in """，,、:：;；‘’'“”""''""":
                    if symbol in e.get("name"):
                        self.send_json_error(message=self.locale.translate('profile_check_char'))
                        return
                if self.get_bit_count(e.get("name"), 40) > 40: # 中文20个包含20个，其他40个
                    self.send_json_error(message=self.locale.translate('profile_check_length'))
                    return

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
                for symbol in """，,、:：;；‘’'“”""''""":
                    if symbol in e.get("name"):
                        self.send_json_error(message=self.locale.translate('profile_check_char'))
                        return
                if self.get_bit_count(e.get("name"), 40) > 40:
                    self.send_json_error(message=self.locale.translate('profile_check_length'))
                    return

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
            parent_code=const.CONSTANT_PARENT_CODE.COMPANY_SCALE, locale=self.locale)
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
            if model.description and len(model.description) > 5000:
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
            parent_code=const.CONSTANT_PARENT_CODE.DEGREE_USER, locale=self.locale)
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
            parent_code=const.CONSTANT_PARENT_CODE.COMPANY_SCALE, locale=self.locale)
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
                for symbol in """，,、:：;；‘’'“”""''""":
                    if symbol in e.get("name"):
                        self.send_json_error(message=self.locale.translate('profile_check_char'))
                        return
                if self.get_bit_count(e.get("name"), 40) > 40:
                    self.send_json_error(message=self.locale.translate('profile_check_length'))
                    return

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
            parent_code=const.CONSTANT_PARENT_CODE.WORK_INTENTION, locale=self.locale)
        salary_list = yield self.dictionary_ps.get_constants(
            parent_code=const.CONSTANT_PARENT_CODE.CURRENT_SALARY_MONTH, locale=self.locale)
        workstate = yield self.dictionary_ps.get_constants(
            parent_code=const.CONSTANT_PARENT_CODE.WORK_STATUS, locale=self.locale)

        constant = ObjectDict()
        constant.worktype_list = worktype_list
        constant.salary_list = salary_list
        constant.workstate_list = workstate

        model = ObjectDict()
        new = False
        locale_display = self.get_current_locale()
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
                    model.position = positions

                cities = intention.cities
                if isinstance(cities, list):
                    for city in cities:
                        city['city_name'] = (CITY.get(
                            city.get('city_name')) if locale_display == "en_US" else CITY_REVERSE.get(
                            city.get('city_name'))) or city.get('city_name')
                model.city_name = cities

                industries = intention.industries
                if industries:
                    for i in industries:
                        i["industry_name"] = (INDUSTRY.get(i.get("industry_name")) if locale_display == "en_US" else (INDUSTRY_REVERSE.get(i.get("industry_name"))) or i.get("industry_name"))

                    model.industry = industries
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


class ProfileImportHandler(BaseHandler):
    """自定义模板简历编辑页面导入"""

    @handle_response
    @authenticated
    @tornado.gen.coroutine
    def get(self):
        company = yield self.company_ps.get_company({'id': self.current_user.wechat.company_id}, need_conf=True)
        current_path = self.request.uri.split('?')[0]
        pid = int(self.params.pid or 0)
        position = yield self.position_ps.get_position(pid, display_locale=self.get_current_locale())
        # 是否需要弹出 隐私协议 窗口
        user_id = self.current_user.sysuser.id
        result, show_privacy_agreement = yield self.privacy_ps.if_privacy_agreement_window(user_id)
        yield self.profile_ps.import_apply_profile(company,position,self.params,self.make_url,current_path,self.current_user,show_privacy_agreement,self.redirect,self.render_page)


class CustomParseIdcardHandler(BaseHandler):
    """自定义简历页: 身份证组件解析"""

    @handle_response
    @authenticated
    @tornado.gen.coroutine
    def post(self):

        if len(self.request.files) == 0:
            file_data = self.request.body
            # file_name = self.get_argument("vfile")
        else:
            image = self.request.files["vfile"][0]
            file_data = image["body"]
            # file_name = image["filename"]
        file_type = filetype(file_content=file_data)
        self.logger.debug("[_upload] file_type: {}".format(file_type))
        if file_type == "unknown":
            self.send_json_error(message="上传的文件类型不支持")
            return
        file_name = self.params.file_name
        side = self.params.side
        file_id = yield self.user_ps.upload_file_server(file_data, file_name, self.current_user.sysuser.id, scene_id=1)  # scene_id=1 ：身份证识别
        if side == "face":
            id_parse = yield self.profile_ps.custom_parse_idcard(file_id.fileId, side, self.current_user.wechat.company_id, self.current_user.sysuser.id)
            if id_parse.code == const.NEWINFRA_API_SUCCESS:
                data = id_parse.data
                idcard = {"name": data.get("name"),
                          "gender": data.get("gender"),
                          "birth": data.get("birth"),
                          "idnumber": data.get("id"),
                          "id_card_addr": data.get("id_card_addr")
                          }
                data["idcard"] = idcard
                self.send_json_success(data=data)
            elif id_parse.code == "PE110002":  # 您今日上传身份证照已超过三次! [需要回填正面照片]
                data = {"idcard": {}, "side": side, "id_photo_url": str(file_id.fileId)}
                self.send_json_error(data=data, message=id_parse.message)
            else:
                self.send_json_error(message=id_parse.message)
        else:
            data = {"idcard": {}, "side": side, "id_photo_url": str(file_id.fileId)}
            self.send_json_success(data=data)
