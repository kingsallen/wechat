# file: useraccounts.struct

namespace java com.moseeker.thrift.gen.useraccounts.struct
namespace py thrift_gen.gen.useraccounts.struct

typedef string Timestamp;


struct Userloginreq {
    1: optional string unionid,
    2: optional string mobile,
    3: optional string password,
    4: optional string code
}

struct Usersetting {
    1: optional i32 id,
    2: optional i32 user_id,
    3: optional string banner_url,
    4: optional i32 privacy_policy
}

/*
  用户实体
*/
struct User {
     1: optional i64        id              ,    // 主key
     2: optional string     username        ,    // 用户名，比如手机号、邮箱等
     3: optional string     password        ,    // 密码
     4: optional i8       is_disable      ,    // 是否禁用，0：可用，1：禁用
     5: optional i64        rank            ,    // 用户等级
     6: optional Timestamp  register_time   ,    // 注册时间
     7: optional string     register_ip     ,    // 注册IP
     8: optional Timestamp  last_login_time ,    // 最近登录时间
     9: optional string     last_login_ip   ,    // 最近登录IP
    10: optional i64        login_count     ,    // 登录次数
    11: optional i64        mobile          ,    // user pass mobile registe
    12: optional string     email           ,    // user pass email registe
    13: optional i8       activation      ,    // is not activation 0:no 1:yes
    14: optional string     activation_code ,    // activation code
    15: optional string     token           ,    // 用户校验token
    16: optional string     name            ,    // 姓名或微信昵称
    17: optional string     headimg         ,    // 头像
    18: optional i64        country_id      ,    // 国家字典表ID, dict_country.id
    19: optional i64        wechat_id       ,    // 注册用户来自于哪个公众号, 0:默认为来自浏览器的用户
    20: optional string     unionid         ,    // 存储仟寻服务号的unionid
    21: optional i8       source          ,    // 来源：0:手机注册, 1:聚合号一键登录, 2:企业号一键登录, 7:PC(正常添加), 8:PC(我要投递), 9: PC(我感兴趣)
    22: optional string     company         ,    // 点击我感兴趣时填写的公司
    23: optional string     position        ,    // 点击我感兴趣时填写的职位
    24: optional i64        parentid             // 合并到了新用户的id
    25: optional i32        email_verified  ,    // 邮箱是否认证
    26: optional string     nickname       	 // 用户昵称
}

/*
  我感兴趣/职位收藏关系表
*/
struct UserFavoritePosition {
    1: optional i64       id              ,       // ID
    2: optional i32       sysuser_id      ,       // 用户ID
    3: optional i32       position_id     ,       // 职位ID
    4: optional i8      favorite        ,       // 0:收藏, 1:取消收藏, 2:感兴趣
    5: optional string    mobile          ,       // 感兴趣的手机号
    6: optional i64       wxuser_id       ,       // wx_user.id
    7: optional i32       recom_id        ,       // 推荐者 fk:wx_user.id
    8: optional Timestamp create_time     ,       //
    9: optional Timestamp update_time             //
}

/*
HR用户实体
*/
struct UserHrAccount{
     1: optional i64               id              , //
     2: optional i64               company_id      , // company.id
     3: optional string            mobile          , // 手机号码
     4: optional string            email           , // 邮箱
     5: optional i64               wxuser_id       , // 绑定的微信账号
     6: optional string            password        , // 登录密码
     7: optional string            username        , // 企业联系人
     8: optional i8              account_type    , // 0 超级账号；1：子账号; 2：普通账号
     9: optional i8              activation      , // 账号是否激活，1：激活；0：未激活
    10: optional i8              disable         , // 1：可用账号；0禁用账号 ） 遵循数据库整体的设计习惯，1表示可用，0表示不可用
    11: optional Timestamp         register_time   , // 注册时间
    12: optional string            register_ip     , // 注册时的IP地址
    13: optional Timestamp         last_login_time , // 最后的登录时间
    14: optional string            last_login_ip   , // 最后一次登录的IP
    15: optional i32               login_count     , // 登录次数
    16: optional i32               source          , // 来源1:雇主 2:官网 3:微信扫描 4:我也要招人(聚合号) 5:我也要招人(企业号)
    17: optional string            download_token  , // 下载行业报告校验码
    18: optional Timestamp         create_time     , // 创建时间
    19: optional Timestamp         update_time       // 修改时间
}

struct DownloadReport {
   1: string code,									//验证码
   2: string company_name,							//公司名称
   3: string mobile,								//手机号码
   4: string name,							//联系人
   5: optional i32 source,							//来源
   6: optional string register_ip,					//注册IP
   7: optional string last_login_ip					//最后登录IP
}

/*
* 帐号绑定
*/
struct BindAccountStruct {
    1: string username,
    2: string password,
    3: optional string member_name,
    4: i8 channel,
    5: i32 appid,
    6: i32 user_id,
    7: i32 company_id,
    8: i32 remainNum,
    9: i32 binding
}

/*
* hr常用筛选条件
*/
struct SearchCondition {
	1: i32 id,
	2: string name, // 名称
	3: i32 publisher, // 发布人
	4: i32 position_id, // 职位id
	5: string keyword, // 关键字
	6: string submit_time, // 发布时间
	7: string work_years, // 工作年限
	8: string city_name, // 城市
	9: string degree, // 学历
   10: string past_position, // 曾任职位
   11: i32 in_last_job_search_position, // 是否只在最近一份工作中搜索曾任职务(0:否，1:是)
   12: i32 min_age, // 最小年龄
   13: i32 max_age, // 最大年龄
   14: string intention_city_name, // 期望城市
   15: i32 sex, // 性别
   16: string intention_salary_code, // 期望薪资
   17: string company_name, // 城市名称
   18: i32 in_last_job_search_company, // 是否只在最近一份工作中搜索公司名称（0:否，1:是）
   19: i32 hr_account_id, // 创建人id(user_hr_account.id)
   20: i32 update_time, // 简历更新时间选项（0：不限，1：最近一周，2：最近两周，3：最近一个月）
   21: i32 type // 类型（0：候选人列表筛选条件，1：人才库列表筛选条件）
}

struct UserEmployeeStruct {
	1: optional i32 id,
	2: optional string employeeid,
	3: optional i32 company_id,
	4: optional i32 role_id,
	5: optional i32 wxuser_id,
	6: optional string ename,
	7: optional i32 position_id,
	8: optional i32 section_id,
	9: optional string custom_field,
	10:optional i64 award
}
struct UserEmployeePointStruct {
   1: optional i32 id,
   2: optional double employee_id,
   3: optional string reason,
   4: optional i32 award,
   5: optional double application_id,
   6: optional double recom_wxuser,
   7: optional double position_id,
   8: optional double berecom_wxuser_id,
   9: optional double award_config_id
}
struct UserEmployeePointSum{
	1: optional i64 award,
	2: optional i64 employee_id
}
/*
 * 个人中心推荐记录
 */
struct ApplicationRecordsForm {
    1: optional i32 id,
    2: optional string position_title,
    3: optional string company_name,
    4: optional string status_name,
    5: optional Timestamp time
}
/*
 * 个人中心职位收藏列表
 */
struct FavPositionForm {
    1: optional i32 id,                 //职位编号
    2: optional string title,           //职位名称
    3: optional string department,      //招聘部门
    4: optional Timestamp time,         //收藏的更新时间
    5: optional string city,            //再招城市
    6: optional i32 salary_top,          //薪资上限
    7: optional i32 salary_bottom,       //薪资下限
    8: optional i8 status,              //薪资下限
    9: optional Timestamp update_time    //职位的更新时间
}

struct RecommendationScoreVO {
    1:i32 link_viewed_count,
    2:i32 interested_count,
    3:i32 applied_count
}

/*
 * 个人中心推荐历史记录信息主体
 */
struct RecommendationRecordVO {
    1: optional i8 recom_status,              //职位编号
    2: optional string applier_name,          //申请人姓名
    3: optional string applier_rel,           //转发者姓名
    4: optional string position,              //职位名称
    5: optional Timestamp click_time,         //点击事件
    6: optional i16 status,                   //招聘进度状态
    7: optional i8 is_interested,             //是否推荐 0没有推荐 1推荐
    8: optional i32 view_number,              //点击次数
    9: optional string headimgurl,            //头像
    10: optional i32 id                       // 推荐记录id
}

/*
 * 查询推荐信息(只有用户是员工时才具备该功能)
 */
struct RecommendationVO {
    1: optional bool hasRecommends,                     //职位编号
    2: optional RecommendationScoreVO score,            //申请编号
    3: optional list<RecommendationRecordVO> recommends //头像
}
/*
 * 个人中心积分记录（只有用户是员工时才具备）
 */
struct AwardRecordForm {
    1: optional i32 id,                //积分记录表编号
    2: optional string reason,         //申请编号
    3: optional string title,          //职位名称
    4: optional Timestamp create_time  //创建时间
}

/*
 * 操作记录
 */
struct ApplicationOperationRecordVO {
    1: optional string date,                    // 操作日期
    2: optional string event,                   // 描述
    3: optional i32 hide,                       // 是否隐藏
    4: optional i32 step_status                 // 状态 2表示拒绝
}

/*
 * 求职记录详情
 */
struct ApplicationDetailVO {
    1: optional i32 pid,                                //积分记录表编号
    2: optional string position_title,                  //申请编号
    3: optional string company_name,                    //职位名称
    4: optional i8 step,                                //进度
    5: optional i8 step_status,                         //状态
    6: optional list<ApplicationOperationRecordVO> status_timeline  //操作记录
}
