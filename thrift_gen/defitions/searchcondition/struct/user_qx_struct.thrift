namespace java com.moseeker.thrift.gen.useraccounts.struct
namespace py thrift_gen.gen.searchcondition.struct.qx_struct

include "./user_search_condition_struct.thrift"
include "./user_collect_position_struct.thrift"

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

struct UserCollectPositionListVO {
    1: optional i32 status,
    2: optional list<user_collect_position_struct.UserCollectPositionDO> userCollectPosition,
    3: optional string message
}

struct UserCollectPositionVO {
    1: optional i32 status,
    2: optional user_collect_position_struct.UserCollectPositionDO userCollectPosition,
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
