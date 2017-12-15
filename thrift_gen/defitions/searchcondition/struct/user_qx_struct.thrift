namespace java com.moseeker.thrift.gen.useraccounts.struct
namespace py thrift_gen.gen.searchcondition.struct.qx_struct

include "./user_search_condition_struct.thrift"
include "./user_collect_position_struct.thrift"

/*
 * 个人中心职位收藏列表
 */
struct CollectPositionForm {
    1: optional i32 id,                 //职位编号
    2: optional string title,           //职位名称
    3: optional string department,      //招聘部门
    4: optional string time,         //收藏的更新时间
    5: optional string city,            //再招城市
    6: optional i32 salary_top,          //薪资上限
    7: optional i32 salary_bottom,       //薪资下限
    8: optional i8 status,              //薪资下限
    9: optional string update_time,    //职位的更新时间
    10: optional string signature        //公众号
}

struct UserSearchConditionListVO {
    1: optional i32 status,
    2: optional list<user_search_condition_struct.UserSearchConditionDO> searchConditionList,
    3: optional string message
}

struct UserSearchConditionVO {
    1: optional i32 status,
    2: optional user_search_condition_struct.UserSearchConditionDO searchCondition,
    3: optional string message
}

struct UserCollectPositionVO {
    1: optional i32 status,
    2: optional user_collect_position_struct.UserCollectPositionDO userCollectPosition,
    3: optional string message
}

struct UserCollectPositionListVO {
    1: optional i32 status,
    2: optional list<CollectPositionForm> userCollectPosition,
    3: optional string message
}

struct UserPositionStatusVO {
    1: optional i32 status,
    2: optional map<i32, i32> positionStatus,
    3: optional string message
}

struct UserViewedPositionVO {
    1: optional i32 status,
    2: optional string message
}
