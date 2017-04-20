# file: profile.thrift

namespace java com.moseeker.thrift.gen.profile.struct
namespace py thrift_gen.gen.profile.struct

/**
 * TODO:list what notation this dateTime represents. eg ISO-8601
 * or if its in the format like YYYY-mm-DD you mentioned.
 */
typedef string Timestamp;

struct Attachment {
    1: optional i32 id,
    2: optional i32 profile_id,
    3: optional string name,
    4: optional string path,
    5: optional string description,
    6: optional Timestamp create_time,
    7: optional Timestamp update_time
}

struct Profile {
    1: optional i32 id,
    2: optional string uuid,
    3: optional i32 lang,
    4: optional i32 source,
    5: optional i32 completeness,
    6: optional i32 user_id,
    7: optional i16 disable,
    8: optional Timestamp create_time,
    9: optional Timestamp update_time
}

struct Awards {
    1: optional i32 id,
    2: optional i32 profile_id,
    3: optional Timestamp reward_date,
    4: optional string name,
    5: optional string award_winning_status,
    6: optional string level,
    7: optional string description,
    8: optional Timestamp create_time,
    9: optional Timestamp update_time
}

struct Basic {
    1: optional i32 profile_id,
    2: optional string name,
    3: optional i16 gender,
    4: optional i32 nationality_code,
    5: optional string nationality_name,
    6: optional i32 city_code,
    7: optional string city_name,
    8: optional Timestamp birth,
    9: optional string weixin,
   10: optional string qq,
   11: optional string motto,
   12: optional string self_introduction,
   13: optional Timestamp create_time,
   14: optional Timestamp update_time
}

struct Credentials {
    1: optional i32 id,
    2: optional i32 profile_id,
    3: optional string name,
    4: optional string organization,
    5: optional string code,
    6: optional string url,
    7: optional Timestamp get_date,
    8: optional string score,
    9: optional Timestamp create_time,
   10: optional Timestamp update_time
}

struct Education {
	1: optional i32 id,
    2: optional i32 profile_id,
    3: optional Timestamp start_date,
    4: optional Timestamp end_date,
    5: optional i16 end_until_now,
    6: optional i32 degree,
    7: optional i32 college_code,
    8: optional string college_name,
    9: optional string college_logo,
    10: optional string major_code,
    11: optional string major_name,
    12: optional string description,
    13: optional i16 is_full,
    14: optional i16 is_unified,
    15: optional i16 is_study_abroad,
    16: optional string study_abroad_country,
    17: optional Timestamp create_time,
    18: optional Timestamp update_time
}

struct ProfileImport {
	1: optional i32 profile_id,
    2: optional i16 source,
    3: optional Timestamp last_update_time,
    4: optional string account_id,
    5: optional string resume_id,
    6: optional string user_name,
    7: optional Timestamp create_time,
    8: optional Timestamp update_time
}

struct Intention {
	1: optional i32 id,
	2: optional i32 profile_id,
    3: optional i32 workstate,
    4: optional i16 salary_type,
    5: optional i32 salary_code,
    6: optional string tag,
    7: optional i16 consider_venture_company_opportunities,
    8: optional Timestamp create_time,
    9: optional Timestamp update_time,
   10: optional i16 worktype,
   11: optional string salary_str,
   12: optional map<string, i32> industries,
   13: optional map<string, i32> positions,
   14: optional map<string, i32> cities
}

struct Language {
	1: optional i32 id,
    2: optional i32 profile_id,
    3: optional string name,
    4: optional i16 level,
    5: optional Timestamp create_time,
    6: optional Timestamp update_time
}

struct CustomizeResume {
    1: optional i32 profile_id,
    2: optional string other,
    3: optional Timestamp create_time,
    4: optional Timestamp update_time
}

struct ProjectExp {
	1: optional i32 id,
	2: optional i32 profile_id,
    3: optional Timestamp start_date,
    4: optional Timestamp end_date,
    5: optional i16 end_until_now,
    6: optional string name,
	7: optional string company_name,
    8: optional i16 is_it,
    9: optional string dev_tool,
    10: optional string hardware,
    11: optional string software,
    12: optional string url,
    13: optional string description,
    14: optional string role,
    15: optional string responsibility,
    16: optional string achievement,
    17: optional string member,
    18: optional Timestamp create_time,
    19: optional Timestamp update_time
}

struct Skill {
	1: optional i32 id,
	2: optional i32 profile_id,
	3: optional string name,
	4: optional i16 level,
	5: optional i16 month,
    6: optional Timestamp create_time,
    7: optional Timestamp update_time
}

struct WorkExp {
	1: optional i32 id,
	2: optional i32 profile_id,
	3: optional Timestamp start_date,
	4: optional Timestamp end_date,
	5: optional i16 end_until_now,
	6: optional i16 salary_type,
	7: optional i32 salary_code,
	8: optional i32 industry_code,
	9: optional string industry_name,
	10: optional i32 company_id,
	11: optional string department_name,
	12: optional i32 position_code,
	13: optional string position_name,
	14: optional string description,
	15: optional i16 type,
	16: optional i32 city_code,
	17: optional string city_name,
	18: optional string report_to,
	19: optional i32 underlings,
	20: optional string reference,
	21: optional string resign_reason,
	22: optional string achievement,
    23: optional Timestamp create_time,
    24: optional Timestamp update_time,
    25: optional string company_name,
    26: optional string company_logo,
    27: optional i16 source,
    28: optional string job
}

struct Works {
	1: optional i32 id,
	2: optional i32 profile_id,
	3: optional string name,
	4: optional string url,
	5: optional string cover,
	6: optional string description,
    7: optional Timestamp create_time,
    8: optional Timestamp update_time
}
