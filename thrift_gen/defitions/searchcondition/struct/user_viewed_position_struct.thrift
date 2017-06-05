namespace java com.moseeker.thrift.gen.dao.struct.userdb
namespace py thrift_gen.gen.searchcondition.struct.userview


struct UserViewedPositionDO {

	1: optional i32 id,	//null
	2: optional i32 userId,	//用户id
	3: optional i32 positionId,	//职位id
	4: optional string createTime	//创建时间

}
