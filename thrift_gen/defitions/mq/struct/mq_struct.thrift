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
    2: optional byte type,
    3: optional i32 sys_template_id,
    4: optional string url,
    5: optional i32 company_id,
    6: optional map<string, MessageTplDataCol> data,
    7: optional byte enable_qx_retry = 1,
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
