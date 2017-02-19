# file: useraccounts.struct

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
    2: optional string title,
    3: optional string department,
    4: optional i8 status,
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
    8: optional Timestamp update_time    //职位的更新时间
}
/*
 * 查询推荐信息(只有用户是员工时才具备该功能)
 */
struct RecommendationForm {
    1: optional i8 recom_status,                //职位编号
    2: optional i32 app_id,                     //申请编号
    3: optional string applier_name,            //申请人姓名
    4: optional string position,                //职位名称
    5: optional Timestamp click_time,           //点击事件
    6: optional Timestamp recom_time,           //推荐事件
    7: optional i16 status,                     //招聘进度状态
    8: optional string recom_2nd_nickname,      //员工二度转发者昵称(标记谁的朋友)可以为空字符串
    9: optional i32 applier_id,                 //申请人的C端账号编号userdb.user_user.id
    10: optional i32 candidate_recom_record_id, //candidatedb.candidate_company.id
    11: optional Timestamp app_time,            //申请时间
    12: optional i8 is_interested,              //是否推荐 0没有推荐 1推荐
    13: optional i32 view_number,               //点击次数
    14: optional string headimgurl              //头像
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
