namespace java com.moseeker.thrift.gen.dao.struct.userdb
namespace py thrift_gen.gen.searchcondition.struct.usersearch


struct UserSearchConditionDO {

	1: optional i32 id,	//null
	2: optional string name,	//筛选项名称
	3: optional string keywords,	//搜索关键字，可添加多个例如（["java", "php"]）
	4: optional string cityName,	//选择城市，可添加多个例如(["上海", "北京"])
	5: optional double salaryTop,	//薪资上限（k）
	6: optional double salaryBottom,	//薪资下限（k）
	7: optional i8 salaryNegotiable,	//薪资面议(0: 否，1：是)
	8: optional string industry,	//所属行业，可添加多个例如(["计算机软件", "金融"])
	9: optional i32 userId,	//user_user.id 用户id
	10: optional i8 disable,	//是否禁用(0: 不禁用，1: 禁用)
	11: optional string createTime,	//创建时间
	12: optional string updateTime	//修改时间

}
