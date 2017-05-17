namespace java com.moseeker.thrift.gen.employee.struct
namespace py thrift_gen.gen.employee.struct

struct Employee {
    1: optional i32 id,
    2: optional string employeeId,
    3: optional i32 companyId,
    4: optional i32 sysuerId,
    5: optional string mobile,
    6: optional i32 wxuserId,
    7: optional string cname,
    8: optional i32 award,
    9: optional bool isRpSent,
    10: optional string customFieldValues,
    11: optional string email,
    12: optional string customField,
    13: optional i32 authMethod
}


enum BindStatus {
    BINDED,
    UNBIND,
    PENDING
}

struct EmployeeResponse {
    1: required BindStatus bindStatus,
    2: optional Employee employee
}


typedef map<string, string> Question;

struct EmployeeVerificationConf {
    1: required i32 companyId,
    2: optional list<string> emailSuffix,
    3: required i16 authMode,
    4: optional string authCode,
    5: optional string custom,
    6: optional list<Question> questions,
    7: optional string customHint,
    8: optional string bindSuccessMessage
}

struct EmployeeVerificationConfResponse {
    1: required bool exists,
    2: optional EmployeeVerificationConf employeeVerificationConf
}

struct Result {
    1: required bool success,
    2: optional string message,
    3: optional i32 employeeId
}

struct EmployeeCustomFieldsConf {
    1: required i32 id,
    2: required i32 companyId,
    3: required string fieldName,
    4: required list<string> fieldValues,
    5: required bool mandatory,
    6: required i32 order
}

enum BindType {
    EMAIL,
    CUSTOMFIELD,
    QUESTIONS
}

struct BindingParams {
    1: required BindType type,
    2: required i32 userId,
    3: required i32 companyId,
    4: optional string email,
    5: optional string mobile,
    6: optional string customField,
    7: optional string name,
    8: optional string answer1,
    9: optional string answer2
}

struct Reward {
    1: optional string reason,
    2: optional i32 points,
    3: optional string updateTime,
    4: optional string title
}

struct RewardConfig {
    1: optional i32 id,
    2: optional i32 points,
    3: optional string statusName
}


struct RewardsResponse {
    1: optional i32 total,
    2: optional list<Reward> rewards,
    3: optional list<RewardConfig> rewardConfigs
}


struct RecomInfo {
    1:  required bool recomed = false,			//推荐状态 true:已推荐 false: 未推荐
	2:  required i32 appId;						//申请ID
	3:  required string applierName;			//申请人姓名
	4:  required string recom2ndNickname;       //员工二度昵称
    5:  required string positionTitle;		    //职位名称
	6:  required string clickTime;				//点击时间
	7:  required string recomTime;				//推荐时间
	8:  required i32 status;					//申请进度 status
	9:  required i32 applierId;					//申请人的 user_id
	10: required i32 applierWxuserId;			//申请人的 user_wx_user.id
	11: required string applierNickname;		//申请人的 user_wx_user.nickname
	12: required i32 candidateRecomRecordId;	//candidate_recom_record.id
	13: required string appTime;				//申请时间
	14: required bool isInterested = false;		// false: 没有求推荐, true: 求推荐
	15: required i32 view_number = 0;          	// 点击次数
	16: required string headimgurl = "";        // 微信头像
}
