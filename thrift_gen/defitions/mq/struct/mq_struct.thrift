namespace java com.moseeker.thrift.gen.mq.struct
namespace py thrift_gen.gen.mq.struct

/*
  消息模板通知数据结构 - data
*/

struct MessageTplDataCol {
    1: optional string color,
    2: optional string value
}

/*
  消息模板通知数据结构
*/
struct MessageTemplateNoticeStruct {
    1: optional i32 user_id,
    2: optional i8 type,
    3: optional i32 sys_template_id,
    4: optional string url,
    5: optional i32 company_id,
    6: optional map<string, MessageTplDataCol> data,
    7: optional i8 enable_qx_retry = 1,
    8: optional i64 delay = 0,
    9: optional string validators,
    10: optional string id
}

struct EmailStruct {
    1: 		i32 user_id,
    2: 		string email,
    3: 		string url,
    4: optional i32 eventType,
    5: optional string subject
}


struct MandrillEmailStruct {
    1: 		string templateName,
    2: 		string to_email,
    3: optional string to_name,
    4: optional	map<string,string> mergeVars,
    5: optional string from_email,
    6: optional string from_name,
    7: optional string subject
}

enum SmsType {
	EMPLOYEE_MERGE_ACCOUNT_SMS,
	RANDOM_SMS,
	RANDOM_PWD_SMS,
	POSITION_FAV_SMS,
	NEW_APPLICATION_TO_HR_SMS,
	NEW_APPLIACATION_TO_APPLIER_SMS,
	APPLICATION_IS_VIEW_SMS,
	APPLICATION_REJECT_SMS,
	APPLICATION_CANCEL_REJECT_SMS,
	APPLICATION_APPROVED_SMS,
	APPLICATION_INTERVIEW_SMS,
	APPLICATION_ENTRY_SMS,
	UPDATE_SYSUSER_SMS,
	REGISTERED_THREE_DAYS_SMS,
	APPLIER_REMIND_EMAIL_ATTACHMENT_SMS,
	APPLIER_REMIND_EMAIL_ATTACHMENT_COM_SMS,
	HR_INVITE_BYPASS_ACCOUNT_SMS,
	HR_BYPASS_ACCOUNT_SMS,
	HR_BYPASS_ACCOUNT_OPEN_SMS,
	HR_BYPASS_ACCOUNT_REJECT_SMS,
	APPLIER_EMAIL_APP_SUC_SMS,
	APPLIER_EMAIL_APP_NO_ATTACH_SMS,
	APPLIER_EMAIL_APP_ATTACH_ERROR_SMS,
	APPLIER_EMAIL_APP_ATTACH_OVERSIZE_SMS,
	APPLIER_EMAIL_APP_RESOLVE_FAIL_SMS,
	APPLIER_EMAIL_APP_ATTACH_RESOLVE_FAIL_SMS,
	APPLIER_APP_ATTACH_RESOLVE_SUC_SMS,
	APPLIER_APP_ATTACH_RESOLVE_FAIL_SMS,
	APPLIER_APP_ATTACH_RESOLVE_ERROR_SMS,
	PPLIER_APP_ATTACH_RESOLVE_OVERSIZE_SMS,
	APPLIER_APP_RESOLVE_FAIL_SMS,
	ALARM_SMS
}
