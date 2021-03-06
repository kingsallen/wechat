# coding=utf-8

import tornado.gen as gen

import conf.path as path
from service.data.base import DataService
from service.data.infra.framework.client.client import ServiceClientFactory
from thrift_gen.gen.common.struct.ttypes import BIZException
from thrift_gen.gen.company.service.CompanyServices import \
    Client as CompanyServicesClient
from util.tool.dict_tool import ObjectDict
from util.tool.http_tool import http_get, unboxing, http_post, http_get_v2, http_put_v2

from conf.newinfra_service_conf.service_info import company_service
from conf.newinfra_service_conf.company import company


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
    def get_oms_all_switch_status(self, company_id):
        """
        获取oms开关状态
        :param company_id: 公司id
        :return:
        """
        params = ObjectDict({
            "companyId": company_id,
            "appid": 102,
        })
        res = yield http_get(path.OMS_SWITCH_ALL, params)
        return res

    @gen.coroutine
    def get_hr_chat_switch_status(self, company_id, candidate_source):
        """
        获取是否显示联系HR的开关配置
        :param company_id:
        :param candidate_source: 0 社招 1 校招 9 全部(显示个人中心首页中我的消息)
        :return:
        """
        mobot_type = {'0': ['社招版MoBot(人工对话模式)', '社招版MoBot(人工+智能对话模式)'],
                      '1': ['校招MoBot(人工对话模式)', '校招MoBot(人工+智能对话模式)'],
                      '9': ['社招版MoBot(人工对话模式)', '社招版MoBot(人工+智能对话模式)',
                            '校招MoBot(人工对话模式)', '校招MoBot(人工+智能对话模式)',
                            '员工版MoBot(人工对话模式)', '员工版MoBot(人工+智能对话模式)']}

        if candidate_source not in ['0', '1', '9']:
            raise gen.Return(False)

        res = yield self.get_oms_all_switch_status(company_id)
        if not res.data:
            self.logger.warning("get_hr_chat_switch_status is null, company.id:{}".format(company_id))
            raise gen.Return(False)

        for product in res.data:
            if product['keyword'] in mobot_type[candidate_source]:
                if product['valid'] == 1:
                    raise gen.Return(True)

        raise gen.Return(False)

    @gen.coroutine
    def get_company_hr_info(self, params):
        """
        根据hrId获取HR信息
        :param params : {'hrId': 123}
        """
        ret = yield http_get_v2(company.COMPANY_HR_INFO, company_service, params)
        return ret

    @gen.coroutine
    def get_company_hr_list(self, params):
        """
        根据hr_ids批量获取HR列表数据
        :param params : [1, 2]
        """
        ret = yield http_put_v2(company.COMPANY_HR_LIST, company_service, params)
        return ret

    @gen.coroutine
    def get_company_list(self, params):
        """
        根据company_ids批量获取公司列表数据
        :param params : [1, 2]
        """
        ret = yield http_put_v2(company.COMPANY_LIST, company_service, params)
        return ret

    @gen.coroutine
    def get_company_conf(self, params):
        """
        根据company_id获取公司列表数据
        :param params : {'companyId': 1}
        """
        ret = yield http_put_v2(company.COMPANY_CONF, company_service, params)
        return ret

    @gen.coroutine
    def batch_get_company_conf(self, company_ids):
        """
        根据company_id获取公司列表数据
        :param params : companyIds: [1, 2, 3]
        """
        params = ObjectDict({
            "companyIds": company_ids,
        })
        ret = yield http_get_v2(company.COMPANY_CONF_BY_COMPANY_IDS, company_service, params)
        return ret

    @gen.coroutine
    def get_company_mobot_conf(self, company_id):
        params = ObjectDict({
            "company_id": company_id,
        })
        res = yield self.get_company_conf(params)
        if not res.data:
            raise gen.Return({})

        mobot_conf_info = ObjectDict(dict(name='', headimg='', welcome=''))
        conf = ObjectDict(res.data)
        mobot_conf_info.name = conf.mobot_name
        mobot_conf_info.headimg = conf.mobot_head_img
        mobot_conf_info.welcome = conf.mobot_welcome

        raise gen.Return(mobot_conf_info)

    @gen.coroutine
    def get_referral_rule_switch(self, company_id):
        params = ObjectDict({
            "company_id": company_id
        })
        ret = yield http_get_v2(company.REFERRAL_RULE_SWITCH, company_service, params)
        return ret

    @gen.coroutine
    def get_nearby_stores(self, params):
        """
        获取用户指定范围内门店位置
        :param params : {'companyId': 123, 'longitude': 120.749991, 'latitude': 30.770423, 'radius': }
        """
        ret = yield http_get_v2(company.COMPANY_NEARBY_STORES, company_service, params)
        return ret

    @gen.coroutine
    def get_position_lbs_info(self, params, pid):
        """
        根据职位id获取职位的LBS信息
        :param params :
        """
        ret = yield http_get_v2(company.COMPANY_POSITION_LBS.format(pid), company_service, params)
        return ret

    @gen.coroutine
    def get_lbs_ip_location(self, remote_ip):
        """
        高德地图ip定位接口： 根据remote_ip获取定位信息：经纬度
        """
        ret = yield http_get(path.LBS_IP_LOCATION.format(remote_ip), infra=False)
        return ret
