# file: company_service.thrift


include "../../common/struct/common_struct.thrift"
include "../struct/company_struct.thrift"

namespace java com.moseeker.thrift.gen.company.service
namespace py thrift_gen.gen.company.service

service CompanyServices {
    common_struct.Response getResource(1:common_struct.CommonQuery query);
    common_struct.Response getResources(1:common_struct.CommonQuery query);
    common_struct.Response getAllCompanies(1:common_struct.CommonQuery query);
    common_struct.Response add(1:company_struct.Hrcompany company);
    common_struct.Response getWechat(1:i64 companyId, 2:i64 wechatId);
    list<company_struct.CompanyForVerifyEmployee> getGroupCompanies(1: i32 companyId) throws (1: common_struct.BIZException e)
    bool isGroupCompanies(1: i32 companyId) throws (1: common_struct.BIZException e)
}
