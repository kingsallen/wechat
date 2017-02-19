namespace java com.moseeker.thrift.gen.dao.struct
namespace py thrift_gen.gen.dao.struct.jobdb

/**
 * TODO:list what notation this dateTime represents. eg ISO-8601
 * or if its in the format like YYYY-mm-DD you mentioned.
 */
typedef string Timestamp;

struct JobApplicationDO {
    1: optional i32 id,                 //编号 唯一标识
    2: optional i32 wechatId,           //微信公众号编号
    3: optional i32 positionId,         //职位编号
    4: optional i32 recommendUserId,    //推荐用户编号user_user.id
    5: optional Timestamp submitTime,   //申请时间
    6: optional i32 statusId,           //申请状态ID（可能已经废弃）
    7: optional i32 lApplicationId,     //ATS的申请ID
    8: optional i32 reward,             //当前申请的积分记录
    9: optional i32 sourceId,           //对应的ATS ID
    10: optional Timestamp createTime,  //创建时间
    11: optional i32 applierId,         //申请人对应的userdb.user_user.id
    12: optional i32 interviewId,       //面试ID（可能已经废弃）
    13: optional string resumeId,       //对应简历数据的编号（mongodb application.id 可能已经废弃）
    14: optional i32 atsStatus,         //ats对接状态
    15: optional string applierName,    //申请者姓名或者微信昵称
    16: optional i32 disable,           //是否有效 0 :有效 1：无效
    17: optional i32 routine,           //申请来源:0 微信端企业号，1：微信端聚合号，10 PC端
    18: optional i32 isViewed,          //申请是否被浏览0 已浏览 1 未浏览
    19: optional i32 notSuitable,       //是否不合适 0 合适 1 不合适
    20: optional i32 companyId,         //公司编号hrdb.hr_company.id
    21: optional Timestamp updateTime,  //修改时间
    22: optional i32 appTplId,          //招聘进度的状态 configdb.config_sys_points_conf_tpl.id
    23: optional i8 proxy,              //是否代理投递 0 正常数据，1代理投递
    24: optional i8 applyType,          //投递区分 0 profile投递，1 email投递 
    25: optional i8 emailStatus,        //email投递状态 0，有效；1,未收到回复邮件；2，文件格式不支持；3，附件超过10M；9，提取邮件失败
    26: optional i32 viewCount          //profile浏览次数
}

struct JobPositionDO {
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
    64: optional i32 teamId                 // 职位所属团队
}
