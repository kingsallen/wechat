namespace java com.moseeker.thrift.gen.dao.service
namespace py thrift_gen.gen.dao.service.userdb

include "../../common/struct/common_struct.thrift"
include "../struct/userdb_struct.thrift"
include "../../useraccounts/struct/useraccounts_struct.thrift"

service UserDBDao {

    list<userdb_struct.UserFavPositionDO> getUserFavPositions(1:common_struct.CommonQuery query);

    //查询用户
    userdb_struct.UserUserDO getUser(1:common_struct.CommonQuery query);

    list<userdb_struct.UserUserDO> listUser(1:common_struct.CommonQuery query);

    //保存用户
    userdb_struct.UserUserDO saveUser(1:userdb_struct.UserUserDO user);

    //查找公司下的HR
    list<userdb_struct.UserHrAccountDO> listHRFromCompany(1: i32 comanyId);

    userdb_struct.UserEmployeeDO getEmployee(1:common_struct.CommonQuery query);

    common_struct.Response putUserEmployee(1: userdb_struct.UserEmployeePointsRecordDO employeeDo);

    common_struct.Response getUserEmployee(1:i32 companyId,2:list<i32> weChatIds);

    common_struct.Response postUserEmployeePoints(1:list<useraccounts_struct.UserEmployeePointStruct> records);

    common_struct.Response getPointSum(1:list<i64> record);

    common_struct.Response putUserEmployees(1:list<useraccounts_struct.UserEmployeeStruct> records);

    common_struct.Response putUserEmployeePoints(1:list<useraccounts_struct.UserEmployeePointStruct> records);

    list<userdb_struct.UserEmployeePointsRecordDO> getUserEmployeePoints(1: i32 employeeId);

    list<userdb_struct.UserEmployeeDO> getUserEmployeesDO(1: common_struct.CommonQuery query)

    common_struct.Response putUserEmployeesDO(1: list<userdb_struct.UserEmployeeDO> employeeDoList)
}
