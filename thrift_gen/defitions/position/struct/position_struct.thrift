# file: profile.thrift

namespace java com.moseeker.thrift.gen.position.struct
namespace py thrift_gen.gen.position.struct

/**
 * TODO:list what notation this dateTime represents. eg ISO-8601
 * or if its in the format like YYYY-mm-DD you mentioned.
 */
typedef string Timestamp

struct Position {
    1:  optional i32 id,
    2:  optional string jobnumber,
    3:  optional i32 company_id,
    4:  optional string title,
    5:  optional string city,
    6:  optional string department,
    7:  optional i32 l_jobid,
    8:  optional string publish_date,
    9:  optional string stop_date,
    10: optional string accountabilities,
    11: optional string experience,
    12: optional string requirement,
    13: optional string language,
    14: optional i32 status,
    15: optional i32 visitnum,
    16: optional i32 source_id,
    17: optional string update_time,
    18: optional i8 employment_type,
    19: optional string hr_email,
    20: optional i32 degree,
    21: optional string feature,
    22: optional i8 candidate_source,
    23: optional string occupation,
    24: optional string industry,
    25: optional i8 email_resume_conf,
    26: optional i32 l_PostingTargetId,
    27: optional i32 priority,
    28: optional i32 share_tpl_id,
    29: optional i32 count,
    30: optional i32 salary_top,
    31: optional i32 salary_bottom,
    32: optional i8 experience_above,
    33: optional i8 degree_above,
    34: optional i8 management_experience,
    35: optional i8 gender,
    36: optional i32 publisher,
    37: optional i32 app_cv_config_id,
    38: optional i32 source,
    39: optional i8 hb_status,
    40: optional i32 age,
    41: optional string major_required,
    42: optional string work_address,
    43: optional string keyword,
    44: optional string reporting_to,
    45: optional i32 is_hiring,
    46: optional i32 underlings,
    47: optional i8 language_required,
    48: optional i32 target_industry,
    49: optional i32 current_status,
    50: optional map<i32, string> cities
}

// 微信端职位列表
struct WechatPositionListQuery {
    1:  optional i32 page_from,
    2:  optional i32 page_size,
    3:  optional string keywords,
    4:  optional string cities,
    5:  optional string industries,
    6:  optional string occupations,
    7:  optional string scale,
    8:  optional string candidate_source,
    9:  optional string employment_type,
    10: optional string experience,
    11: optional string salary,
    12: optional string degree,
    13: optional i32 company_id,
    14: optional i32 did,
    15: optional string department
    16: optional bool order_by_priority,
    17: optional string custom
}

struct WechatPositionListData {
    1:  required i32 id,
    2:  required string title,
    4:  optional i32 salary_top,
    5:  optional i32 salary_bottom,
    6:  required string publish_date,
    7:  required string department,
    8:  required i32 visitnum,
    9:  required bool in_hb,
    10: required i32 count,
    11: required string company_abbr,
    12: required string company_logo,
    13: required string company_name,
    14: required bool is_new,
    15: required string city
}

// 微信端职位列表的附加红包信息
struct RpExtInfo {
    1: required i32 pid,
    2: required i32 remain,
    3: required bool employee_only
}

// 微信端红包活动职位列表
struct WechatRpPositionListData {
    1:  required i32 id,
    2:  required string title,
    3:  required bool fixed,
    4:  optional i32 salary_top,
    5:  optional i32 salary_bottom,
    6:  required string publish_date,
    7:  required string department,
    8:  required i32 visitnum,
    9:  required bool in_hb,
    10: required i32 count,
    11: required string company_abbr,
    12: required string company_logo,
    13: required string company_name,
    14: required bool is_new
    15: required i32 remain,
    16: required bool employee_only,
    17: required string city
}

// 微信端获取红包分享信息
struct WechatShareData {
    1: required string cover,
    2: required string title,
    3: required string description,
}

//第三方自定义职能
struct JobOccupationCustom {
    1: optional i32 id,
    2: optional string name
}

//第三方渠道职位，用于职位同步
struct ThirdPartyPositionForSynchronization {
    1:  string title,
    2:  string category_main_code,
    3:  string category_main,
    4:  string category_sub_code,
    5:  string category_sub,
    6:  string quantity,
    7:  string degree_code,
    8:  string degree,
    9:  string experience_code,
    10: string experience,
    11: string salary_low,
    12: string salary_high,
    13: string description,
    14: string pub_place_code,
    15: i32 position_id,
    16: string work_place,
    17: string email,
    18: string stop_date,
    19: i32 channel,
    20: string type_code,
    21: string job_id,
    22: string pub_place_name
}

struct ThirdPartyPositionForSynchronizationWithAccount {
    1: string user_name,
    2: string password,
    3: string member_name,
    4: string position_id,
    5: string channel,
    6: ThirdPartyPositionForSynchronization position_info
}
