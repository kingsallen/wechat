# coding=utf-8

import tornado.gen as gen

import conf.alphacloud_api as api
import conf.path as path
from service.data.base import DataService
from service.data.infra.framework.client.client import ServiceClientFactory
from thrift_gen.gen.common.struct.ttypes import BIZException
from thrift_gen.gen.company.service.CompanyServices import \
    Client as CompanyServicesClient
from util.tool.dict_tool import ObjectDict
from util.tool.http_tool import http_get, unboxing, http_post, http_get_clound


class InfraCompanyDataService(DataService):

    company_services_client = ServiceClientFactory.get_service(CompanyServicesClient)

    @gen.coroutine
    def get_company_by_id(self, params):
        res = yield http_get(path.COMPANY, params)
        return unboxing(res)

    @gen.coroutine
    def get_company_all(self, params):
        res = yield http_get(path.COMPANY_ALL, params)
        return unboxing(res)

    @gen.coroutine
    def create_company_on_wechat(self, params):
        res = yield http_post(path.COMPANY, params)
        return unboxing(res)

    @gen.coroutine
    def create_company(self, params):
        res = yield http_post(path.CREATE_COMPANY, params)
        raise gen.Return(res)

    @gen.coroutine
    def belongs_to_group_company(self, company_id) -> bool:
        try:
            res = yield self.company_services_client.isGroupCompanies(int(company_id))
        except BIZException as e:
            self.logger.debug("%s - %s" % (e.code, e.message))
            return False
        else:
            return res

    @staticmethod
    def _thrift_companys_to_dict(thrift_companys):
        """将基础服务返回的对象转换成 ObjecitDict，
        会过滤掉没有 signature 的元素
        （这种情况在数据正常的时候很难发生，但是为了预防 bug，先下手为强）
        """
        for c in thrift_companys:
            if c.signature:
                yield ObjectDict(id=c.id, name=c.name,
                                 abbreviation=c.abbreviation,
                                 signature=c.signature)

    @gen.coroutine
    def get_group_company_list(self, company_id) -> list:
        try:
            res = yield self.company_services_client.getGroupCompanies(
                int(company_id))
        except BIZException as e:
            self.logger.debug("%s - %s" % (e.code, e.message))
            return []
        else:
            return list(self._thrift_companys_to_dict(res))

    @gen.coroutine
    def get_only_referral_reward(self, company_id):
        params = ObjectDict({
            "company_id": company_id
        })
        res = yield http_get(path.ONLY_REFERRAL_REWARD, params)
        return res

    @gen.coroutine
    def get_crucial_info_state(self, company_id):
        """
         获取推荐人才关键信息开关状态
        :param company_id:
        :return:

        """
        params = ObjectDict({
            "company_id": company_id,
        })
        res = yield http_get(path.INFRA_REFERRAL_CRUCIAL_INFO_SWITCH, params)
        return res

    @gen.coroutine
    def get_company_mobot_conf(self, company_id):
        params = ObjectDict({
            "company_id": company_id,
        })
        res = yield http_get(path.MOBOT_IMAGE, params)
        return res

    @gen.coroutine
    def check_oms_switch_status(self, company_id, module_name):
        """
        检查oms控制的一系列开关状态
        :param company_id: 公司id
        :param module_name: 需检查开关的模块名
        :return:
        """
        params = ObjectDict({
            "companyId": company_id,
            "moduleName": module_name
        })
        res = yield http_get(path.OMS_SWITCH, params)
        return res

    @gen.coroutine
    def get_company_hr_info(self, params):
        """
        根据hrId获取HR信息

        :param params : {'hrId': 123}
        :return:
        {
            "code": "0",
            "message": "操作成功",
            "data": {
                "id": 82752,
                "companyId": 39978,
                "mobile": "18365251623",
                "email": "zangxi@moseeker.com",
                "wxuserId": null,
                "password": "e8374a97f36a5d57dd16060fc8d619b3b4283592",
                "username": "沙盒测试主账号",
                "accountType": 0,
                "activation": 1,
                "disable": 1,
                "registerTime": "2016-07-20 14:31:05",
                "registerIp": "182.92.169.77",
                "lastLoginTime": "2019-08-29 14:38:42",
                "lastLoginIp": "116.236.170.42",
                "loginCount": 8698,
                "source": 1,
                "downloadToken": null,
                "createTime": "2016-07-20 14:31:05",
                "updateTime": "2019-08-29 15:00:08",
                "headimgurl": "https://cdn-t.dqprism.com/upload/../../8d3156ba-62b6-4879-b5e7-ae2618126895.phpundefined",
                "leaveToMobot": 0,
                "remarkName": "",
                "applicationPositionCountFlag": 0
            }
        }
        """
        ret = yield http_get_clound(api.company_service.api.CLOUD_GET_COMPANY_HR_INFO, api.company_service.service, params)
        return ret
