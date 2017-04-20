namespace java com.moseeker.thrift.gen.dao.struct
namespace py thrift_gen.gen.dao.struct.candidatedb

/**
 * TODO:list what notation this dateTime represents. eg ISO-8601
 * or if its in the format like YYYY-mm-DD you mentioned.
 */
typedef string Timestamp;

exception CURDException {
    1: i32 code,
    2: string message
}

/*
 * 候选人记录
 */
struct CandidateCompanyDO {
    1: optional i32 id,                     // 数据库编号
    2: optional i32 companyId,              // 公司编号 hrdb.hr_company.id
    3: optional Timestamp updateTime,       // 修改时间
    4: optional i8 status,                  // 状态 0：不是候选人，1：候选人
    5: optional bool isRecommend,           // 是否推荐 false:未推荐，true:推荐
    6: optional string name,                // 姓名或微信昵称
    7: optional string email,               // 邮箱
    8: optional string mobile,              // 手机号码
    9: optional string nickname,            // 昵称
    10: optional string headimgurl,         // 头像
    11: optional i32 sysUserId,          // userdb.user_user.id C端账号编号，表示该候选人绑定的C端账号
    12: optional i8 clickFrom           // 点击入口0:未知, 朋友圈(timeline ) 1, 微信群(groupmessage) 2, 个人消息(singlemessage)
}

/**
 * 候选人浏览职位记录
 */
struct CandidatePositionDO {
    1: optional i32 positionId,             // 职位编号jobdb.job_position.id
    2: optional Timestamp updateTime,       // 修改时间
    3: optional bool isInterested,          // 是否感兴趣 0：不感兴趣，1：感兴趣 
    5: optional i32 candidateCompanyId,     // 候选人编号candidatedb.candidate_company.id
    6: optional i32 viewNumber,             // 候选人浏览职位次数
    7: optional i8 sharedFromEmployee,      // 是否是员工转发 0：不是员工转发，1：员工转发
    8: optional i32 userId                  // 员工编号
}

/**
 * 职位转发记录
 */
struct CandidatePositionShareRecordDO {
    1: optional i32 id,                     // 数据库编号
    2: optional i32 wechatId,               // 所属公众号 
    3: optional i32 positionId,             // 职位编号 jobdb.job_position.id
    4: optional i32 recomUserId,            // 转发者的C端账号编号 userdb.user_user.id
    5: optional i32 viewerId,               // userdb.user_wx_viewer.id 浏览用户ID
    6: optional string viewerIp,            // 浏览着的IP地址
    7: optional i8 source,                  // 浏览者来源
    8: optional Timestamp createTime,       // 记录创建时间
    9: optional Timestamp updateTime,       // 记录修改时间
    10: optional i32 presenteeUserId,       // 查看着的C端账号编号 userdb.user_user.id
    11: optional i8 clickFrom               // 点击来源
}

/**
 * 候选人转发记录
 */
struct CandidateRecomRecordDO {
    1: optional i32 id,                     // 数据库编号
    2: optional i32 appId,                  // job_application.id, 被推荐者申请ID
    3: optional i32 positionId,             // 职位编号 jobdb.job_position.id
    4: optional Timestamp clickTime,        // 职位点击时间
    5: optional i32 depth,                  // 链路深度
    6: optional string realname,            // 真实姓名
    7: optional string company,             // 公司名称
    8: optional string position,            // 记录创建时间
    9: optional string recomReason,         // 推荐理由
    10: optional Timestamp recomTime,       // 推荐时间
    11: optional i8 isRecom,                // 推荐状态，0：推荐过，1：未推荐,2:忽略--推荐被动求职者时，可以选中多个求职者挨个填写求职者信息。忽略是指跳过当前求职者，到下一个求职者。3： 选中--推荐被动求职者时，可以选中多个被动求职者。
    12: optional Timestamp createTime,      // 记录创建时间
    13: optional Timestamp updateTime,      // 记录修改时间
    14: optional string mobile,             // 手机号码
    15: optional i32 presenteeUserId,       // userdb.user_user.id 被推荐者的C端账号编号
    16: optional i32 repostUserId,          // 第2度人脉推荐人C 端账号编号，用来标记谁的朋友
    17: optional i32 postUserId             // userdb.user_user.id 推荐者的C端账号编号
}

/**
 * 候选人信息详情
 */
struct CandidateRemarkDO {
    1: optional i32 id,                         // 数据库编号
    2: optional i32 hraccountId,                // 做候选人标记的账号编号 hr_account.id
    3: optional i8 gender,                      // 0：未知，1：男，2：女
    4: optional i8 age,                         // 年龄
    5: optional string mobile,                  // 手机号码
    6: optional string email,                   // 邮箱
    7: optional string currentCompany,          // 现处公司
    8: optional string currentPosition,         // 职务
    9: optional string education,               // 毕业院校
    10: optional string degree,                 // 学历
    11: optional Timestamp graduateAt,          // 毕业时间
    12: optional bool isStar,                   // 0: 星标 1: 没有星标
    13: optional string remark,                 // 备注
    14: optional Timestamp createTime,          // 记录创建时间
    15: optional Timestamp updateTime,          // 修改时间
    16: optional i8 status,                     // 0: 新数据 1: 正常 2:被忽略
    17: optional string name,                   // 候选人姓名
    18: optional i32 userId                    // userdb.user_user.id 被推荐者的C端账号
}

/**
 * 候选人转发链路记录
 */
struct CandidateShareChainDO {
    1: optional i32 id,                         // 数据库编号
    2: optional i32 positionId,                 // jobdb.job_position.id,相关职位 id
    3: optional i32 rootRecomUserId,            // userdb.user_user.id,最初转发人的 user_user.id
    4: optional i32 root2RecomUserId,           // userdb.user_user.id,最初转发人后一个的 user_user.id
    5: optional i32 recomUserId,                // userdb.user_user.id,转发人的 user_user.id
    6: optional i32 presenteeUserId,            // userdb.user_user.id,点击者 user_id
    7: optional i16 depth,                      // 第几层关系, 默认从 1 开始,当 presentee_id 是员工时,depth 为 0,表示该员工把链路截断了
    8: optional i32 parentId,                   // candidatedb.candidate_share_chain.id,上一条 share_chain.id
    9: optional Timestamp clickTime,            // candidatedb.candidate_position_share_record.click_time,点击时间
    10: optional Timestamp createTime          // 创建时间 
}

/**
 * HR标注的推荐职位
 */
struct CandidateSuggestPositionDO {
    1: optional i32 id,                         // 数据库编号
    2: optional i32 hraccountId,                // 做职位推荐的账号编号 userdb.user_hr_account.id
    3: optional i32 positionId,                 // 职位编号jobdb.job_position.id
    4: optional i32 userId,                     // userdb.user_user.id C端账号编号
    5: optional bool disable,                   // 是否生效 0：生效 1：不生效
    6: optional Timestamp createTime,           // 创建时间
    7: optional Timestamp updateTime            // 修改时间
}
