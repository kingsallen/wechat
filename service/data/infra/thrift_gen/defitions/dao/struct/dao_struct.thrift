namespace java com.moseeker.thrift.gen.dao.struct
namespace py thrift_gen.gen.dao.struct.dao
/**
 * TODO:list what notation this dateTime represents. eg ISO-8601
 * or if its in the format like YYYY-mm-DD you mentioned.
 */
typedef string Timestamp;

enum ConditionType {
    AndType,
    OrType,
    MoreThanType,
    LessThanType,
    BetweenType
}

struct Condition {
    1: optional ConditionType conditionType,
    2: optional Condition condition,
    3: optional list<string> params
}

struct WordpressPosts { 
    1: i64 id,
    2: i64 postAuthor,
    3: string postDate,
    4: string postContent,
    5: string postTitle,
    6: string postExcerpt,
    7: string postStatus,
    8: string postModified,
    9: string version,
    10: string plateform,
    11: string postName
}

struct WordpressTermRelationships { 
    1: i64 objectId,
    2: i64 termTaxonomyId
}

struct PostExt { 
    1: i64 objectId,
    2: string version,
    3: string platform
}

//第三方帐号
struct ThirdPartAccountData{
        1: i32 id,
        2: string name,
        3: i32 channel,
        4: string username,
        5: string password,
        6: string membername,
        7: i32 binding,
        8: i32 company_id,
        9: i32 remain_num,
        10: Timestamp sync_time
}
//第三方渠道职位
struct ThirdPartyPositionData {
	1: i32 id,
	2: i32 position_id,
	3: string third_part_position_id,
	4: i8 channel,
	5: i8 is_synchronization,
	6: i8 is_refresh,
	7: string sync_time,
	8: string refresh_time,
	9: string update_time,
	10: string occupation,
	11: string address,
	12: string sync_fail_reason
}
struct HRCompanyConfData{
    1:i32 company_id,
    2:i32 theme_id,
    3:i32 hb_throttle,
    4:string app_reply,
    5:string job_custom_title,
    6:string job_occupation
}
struct HistoryOperate{
	1: optional i32 id,
	2: optional i64 app_id,
	3: optional i32 operate_tpl_id,
	4: optional i32 recruit_order
}
