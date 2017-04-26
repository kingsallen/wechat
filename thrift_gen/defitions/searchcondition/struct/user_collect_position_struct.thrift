namespace java com.moseeker.thrift.gen.dao.struct.userdb
namespace py thrift_gen.gen.searchcondition.struct.usercollect


struct UserCollectPositionDO {

	1: optional i32 id,	//null
	2: optional i32 userId,	//用户id
	3: optional i32 positionId,	//职位id
	4: optional i32 status,	//0:收藏, 1:取消收藏
	5: optional string createTime,	//创建时间
	6: optional string updateTime	//修改时间

}
