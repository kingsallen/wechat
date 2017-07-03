# coding=utf-8

import tornado.gen as gen

import conf.path as path
from service.data.base import DataService
from service.data.infra.framework.client.client import ServiceClientFactory
from thrift_gen.gen.common.struct.ttypes import BIZException
from thrift_gen.gen.company.service.CompanyServices import \
    Client as CompanyServicesClient
from util.tool.dict_tool import ObjectDict
from util.tool.http_tool import http_get, unboxing, http_post


class InfraCompanyDataService(DataService):

    company_services_client = ServiceClientFactory.get_service(CompanyServicesClient)

    @gen.coroutine
    def get_company_all(self, params):
        res = yield http_get(path.COMPANY_ALL, params)
        return unboxing(res)

    @gen.coroutine
    def create_company_on_wechat(self, params):
        res = yield http_post(path.COMPANY, params)
        return unboxing(res)

    @gen.coroutine
    def belongs_to_group_company(self, company_id) -> bool:
        res = False
        try:
            res = yield self.company_services_client.isGroupCompanies(int(company_id))
        except BIZException as e:
            res = False
            if e.code == 90010:
                self.logger.debug("[infra belongs_to_group_company]: company_id: %s does not exist!" % company_id)
            else: raise
        except Exception:
            raise
        else:
            return res

    @staticmethod
    def _thrift_companys_to_dict(thrift_companys):
        for c in thrift_companys:
            dc = ObjectDict(name=c.name, id=c.id, abbreviation=c.abbreviation, signature=c.signature)
            yield dc

    @gen.coroutine
    def get_group_company_list(self, company_id) -> list:
        res = []
        try:
            res = yield self.company_services_client.getGroupCompanies(int(company_id))
        except BIZException as e:
            res = []
            if e.code == 32010:
                self.logger.debug( "[infra get_group_company_list]: company_id: %s does not belong to a group company!" % company_id)
            else: raise
        except Exception:
            raise
        else:
            return list(self._thrift_companys_to_dict(res))

