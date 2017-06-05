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
    1:  optional i32 id,
    2:  optional string title,
    4:  optional i32 salary_top,
    5:  optional i32 salary_bottom,
    6:  optional string publish_date,
    7:  optional string department,
    8:  optional i32 visitnum,
    9:  optional bool in_hb,
    10: optional i32 count,
    11: optional string company_abbr,
    12: optional string company_logo,
    13: optional string company_name,
    14: optional bool is_new,
    15: optional string city,
    16: optional i32 priority
}

// 微信端职位列表的附加红包信息
struct RpExtInfo {
    1: optional i32 pid,
    2: optional i32 remain,
    3: optional bool employee_only
}

// 微信端红包活动职位列表
struct WechatRpPositionListData {
    1:  optional i32 id,
    2:  optional string title,
    3:  optional bool fixed,
    4:  optional i32 salary_top,
    5:  optional i32 salary_bottom,
    6:  optional string publish_date,
    7:  optional string department,
    8:  optional i32 visitnum,
    9:  optional bool in_hb,
    10: optional i32 count,
    11: optional string company_abbr,
    12: optional string company_logo,
    13: optional string company_name,
    14: optional bool is_new
    15: optional i32 remain,
    16: optional bool employee_only,
    17: optional string city
}

// 微信端获取红包分享信息
struct WechatShareData {
    1: optional string cover,
    2: optional string title,
    3: optional string description,
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

/* Gamma 0.9*/
// 职位详情
struct PositionDetails{
      1: optional i32 id,                     //数据库标志
      2: optional string jobnumber,           //用户上传的职位编号
      3: optional i32 companyId,              //职位所属公司编号hrdb.hr_company.id
      4: optional string title,               // 职位标题
      5: optional string city,                //职位指定的城市信息（真正的城市数据在职位城市关系表中）
      6: optional string department,          //职位指定的所属部门
      7: optional i32 lJobid,                 //ATS对接的其他平台的职位标志
      8: optional string publishDate,         //发布日期
      9: optional string stopDate,            // 截止日期（新功能的职位下线是按照职位状态，并且也兼容这个字段）
      10: optional string accountabilities,   // 职位描述
      11: optional string experience,         // 经验要求
      12: optional string requirement,        // 任职条件
      13: optional string salary,             // 薪资(废弃)
      14: optional string language,           // 语言
      15: optional string jobGrade,           // 优先级
      16: optional i32 status,                // 状态 0 有效, 1 删除, 2 撤下
      17: optional i32 visitnum,              // 查看次数
      18: optional string lastvisit,          // 最后一个访问者 weixin openid
      19: optional i32 source_id,              // 职位来源 0 : moseeker
      20: optional Timestamp updateTime,      // 修改时间
      21: optional string businessGroup,      // 事业群
      22: optional i8 employmentType,         // 0:全职，1：兼职：2：合同工 3:实习 9:其他
      23: optional string hrEmail,            // HR联系人邮箱，申请通知
      24: optional string benefits,           // 职位福利
      25: optional i8 degree,                 // 0:无 1:大专 2:本科 3:硕士 4:MBA 5:博士 6:中专 7:高中 8: 博士后 9:初中
      26: optional string feature,            // 职位特色，多福利特色使用#分割
      27: optional bool emailNotice,          // 申请后是否给 HR 发送邮件 0:发送 1:不发送
      28: optional i8 candidateSource,        // 0:社招 1：校招 2:定向招聘
      29: optional string occupation,         // 职位职能
      30: optional bool isRecom,              // 是否需要推荐0：需要 1：不需要
      31: optional string industry,           // 所属行业
      32: optional i32 hongbaoConfigId,       // 红包配置编号
      33: optional i32 hongbaoConfigRecomId,  // 红包配置推荐编号
      34: optional i32 hongbaoConfigAppId,    // 红包配置推荐编号
      35: optional bool emailResumeConf,      // 0:允许使用email简历进行投递；1:不允许使用email简历投递
      36: optional i32 lPostingTargetId,      // lumesse每一个职位会生成一个PostingTargetId,用来生成每个职位的投递邮箱地址
      37: optional i8 priority,               // 排序权重
      38: optional i32 shareTplId,            // 分享分类0:无1:高大上2：小清新3：逗比
      39: optional string district,           // 添加区(省市区的区)
      40: optional i16 count,                 // 招聘人数
      41: optional i32 salaryTop,             // 薪资上限
      42: optional i32 salaryBottom,          // 薪资下限
      43: optional bool experienceAbove,      // 及以上 1：需要， 0：不需要
      44: optional bool degreeAbove,          // 及以上 1：需要， 0：不需要
      45: optional bool managementExperience, // 是否要求管理经验0：需要1：不需要
      46: optional i8 gender,                 // 0-> female, 1->male, 2->all
      47: optional i32 publisher,             // 职位发布人
      48: optional i32 appCvConfigId,         // 职位开启并配置自定义模板 hr_app_cv_conf.id
      49: optional i16 source,                // 0:手动创建, 1:导入, 9:ATS导入
      50: optional i8 hbStatus,               // 否正参加活动：0=未参加  1=正参加点击红包活动  2=正参加被申请红包活动  3=正参加1+2红包活动
      52: optional i32 childCompanyId,        // hr_child_company.id
      53: optional i8 age,                    // 年龄要求, 0：无要求
      54: optional string majorRequired,      // 专业要求
      55: optional string workAddress,        // 上班地址
      56: optional string keyword,            // 职位关键词
      57: optional string reportingTo,        // 汇报对象
      58: optional bool isHiring,             // 是否急招, 1:是 0:否
      59: optional i16 underlings,            // 下属人数， 0:没有下属
      60: optional bool languageRequired,     // 语言要求，1:是 0:否
      61: optional i32 targetIndustry,        // 期望所在的行业
      62: optional i8 currentStatus,          // 0:招募中, 1: 未发布, 2:暂停, 3:撤下, 4:关闭
      63: optional i16 positionCode,          // 职能字典code, dict_position.code
      64: optional string resUrl,             // 职位图片
      65: optional i32 teamId,                // 职位所属团队
      66: optional string teamName            // 团队名称
      67: optional string teamDescription     // 团队描述
}

struct PositionDetailsVO{
    1:i32 status,
    2:PositionDetails data,
    3:string message
}

struct PositionDetailsListVO{
    1:i32 status,
    2:list<PositionDetails> data,
    3:string message,
    4:i32 per_age, // 每页多少条 默认10条
    6:i32 page // 当前第几页
}
