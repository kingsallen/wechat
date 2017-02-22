# file: userbs_service.thrift

include "../../common/struct/common_struct.thrift"
include "../../useraccounts/struct/bindtype_struct.thrift"

namespace java com.moseeker.thrift.gen.apps.userbs.service
namespace py thrift_gen.gen.apps.userbs.service

/**
 * TODO:list what notation this dateTime represents. eg ISO-8601
 * or if its in the format like YYYY-mm-DD you mentioned.
 */

service UserBS {
	//账号绑定
	common_struct.Response bindOnAccount(1: i32 appid, 2: string unionid, 3: string code, 4: string mobile, 5: bindtype_struct.BindType bindType);
}
