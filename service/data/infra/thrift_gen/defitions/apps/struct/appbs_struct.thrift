namespace py thrift_gen.gen.apps.positionbs.struct

typedef string Timestamp

/*
* 申请记录实体
*
*/
struct ThirdPartyPosition {
     1: optional i32 salary_top,             // 薪资上限
     2: optional i32 salary_bottom,          // 薪资下限
     3: optional i32 count,            	     // 招聘人数
     4: optional string address,             // 工作地址
     5: optional bool use_company_address,   // 是否使用公司地址
     6: optional string occupation_level1,   // 倒数第二级的第三方职位职能
     7: optional string occupation_level2,   // 最后一级的第三方职位职能
     8: optional byte channel               // 渠道
}

struct ThirdPartyPositionForm {
    1: i32 position_id,				//职位编号
    2: i32 appid,				//调用方编号
    3: list<ThirdPartyPosition> channels	//渠道参数
}
