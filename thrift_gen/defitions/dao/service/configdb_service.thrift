namespace java com.moseeker.thrift.gen.dao.service
namespace py thrift_gen.gen.dao.service.configdb

include "../../common/struct/common_struct.thrift"
include "../struct/configdb_struct.thrift"

service ConfigDBDao {
	list<configdb_struct.ConfigSysPointConfTplDO> getAwardConfigTpls(1:common_struct.CommonQuery query);
    common_struct.Response getConfigSysPointsConfTpls(1:common_struct.CommonQuery query);
    common_struct.Response getConfigSysPointsConfTpl(1:common_struct.CommonQuery query);
    common_struct.Response getRecruitProcesses(1:i32 companyId);
}
