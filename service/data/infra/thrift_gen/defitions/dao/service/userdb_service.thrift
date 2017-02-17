namespace java com.moseeker.thrift.gen.dao.service
namespace py thrift_gen.gen.dao.service.userdb

include "../../common/struct/common_struct.thrift"
include "../struct/userdb_struct.thrift"
include "../../useraccounts/struct/useraccounts_struct.thrift"

service UserDBDao {
    list<userdb_struct.UserFavPositionDO> getUserFavPositions(1:common_struct.CommonQuery query);
    
    //查询用户
    userdb_struct.UserUserDO getUser(1:common_struct.CommonQuery query);
    //保存用户
    userdb_struct.UserUserDO saveUser(1:userdb_struct.UserUserDO user);

    userdb_struct.UserEmployeeDO getEmployee(1:common_struct.CommonQuery query);
    common_struct.Response getUserEmployee(1:i32 companyId,2:list<i32> weChatIds);
    common_struct.Response postUserEmployeePoints(1:list<useraccounts_struct.UserEmployeePointStruct> records);
    common_struct.Response getPointSum(1:list<i64> record);
    common_struct.Response putUserEmployees(1:list<useraccounts_struct.UserEmployeeStruct> records);
    common_struct.Response putUserEmployeePoints(1:list<useraccounts_struct.UserEmployeePointStruct> records);
    list<userdb_struct.UserEmployeePointsRecordDO> getUserEmployeePoints(1: i32 employeeId);
}
