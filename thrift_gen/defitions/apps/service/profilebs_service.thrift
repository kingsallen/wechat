# file: profile_service.thrift

include "../../common/struct/common_struct.thrift"

namespace java com.moseeker.thrift.gen.apps.profilebs.service
namespace py thrift_gen.gen.apps.profilebs.service

/**
 * TODO:list what notation this dateTime represents. eg ISO-8601
 * or if its in the format like YYYY-mm-DD you mentioned.
 */

service ProfileBS {
   	//简历回收
	common_struct.Response retrieveProfile(1:i32 positionId, 2:i32 channel, 3:string profile);
	//简历进度
	common_struct.Response profileProcess(1:i32 company_id, 2:i32 progress_status, 3:string aids,4:i32 account_id);
	//ats简历进度
	common_struct.Response profileProcessAts(1:i32 progress_status, 2:string aids);
}

