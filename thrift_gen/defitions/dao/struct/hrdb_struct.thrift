namespace java com.moseeker.thrift.gen.dao.struct
namespace py thrift_gen.gen.dao.struct.hrdb

/**
 * TODO:list what notation this dateTime represents. eg ISO-8601
 * or if its in the format like YYYY-mm-DD you mentioned.
 */
typedef string Timestamp

struct HrOperationRecordDO {
    1: optional double adminId,
    2: optional double companyId,
    3: optional double appId,
    4: optional double statusId,
    5: optional i32 operateTplId,
    6: optional string optTime 
}

struct HrHbConfigDO {
    1:  optional i32 id,
    2:  optional i32 type,
    3:  optional i32 target,
    4:  optional i32 company_id,
    5:  optional Timestamp start_time,
    6:  optional Timestamp end_time,
    7:  optional i32 total_amount,
    8:  optional double range_min,
    9:  optional double range_max,
    10: optional i32 probability,
    11: optional i32 d_type,
    12: optional string headline,
    13: optional string headline_failure,
    14: optional string share_title,
    15: optional string share_desc,
    16: optional string share_img,
    17: optional i32 status,
    18: optional i32 checked,
    19: optional i32 estimated_total,
    20: optional Timestamp create_time,
    21: optional Timestamp update_time,
    22: optional i32 actual_total
}

struct HrHbPositionBindingDO {
    1: optional i32 id,
    2: optional i32 hb_config_id,
    3: optional i32 position_id,
    4: optional i32 trigger_way,
    5: optional double total_amount,
    6: optional i32 total_num,
    7: optional Timestamp create_time,
    8: optional Timestamp update_time
}

struct HrHbItemsDO {
    1:  optional i32 id,
    2:  optional i32 hb_config_id,
    3:  optional i32 binding_id,
    4:  optional i32 index,
    5:  optional double amount,
    6:  optional i32 status,
    7:  optional i32 wxuser_id,
    8:  optional Timestamp open_time,
    9:  optional Timestamp create_time,
    10: optional Timestamp update_time,
    11: optional i32 trigger_wxuser_id
}

struct HrHbScratchCardDO {
    1:  optional i32 id,
    2:  optional i32 wechat_id,
    3:  optional string cardno,
    4:  optional i32 status,
    5:  optional double amount,
    6:  optional i32 hb_config_id,
    7:  optional string bagging_openid,
    8:  optional Timestamp create_time,
    9:  optional i32 hb_item_id,
    10: optional i32 tips
}

struct HrHbSendRecordDO {
    1:  optional i32 id,
    2:  optional string return_code,
    3:  optional string return_msg,
    4:  optional string sign,
    5:  optional string resule_code,
    6:  optional string err_code,
    7:  optional string err_code_des,
    8:  optional string mch_billno,
    9:  optional string mch_id,
    10: optional string wxappid,
    11: optional string re_openid,
    12: optional string total_amount,
    13: optional string send_time,
    14: optional string send_listid,
    15: optional Timestamp create_time,
    16: optional i32 hb_item_id
}

struct HrEmployeeCertConfDO {
    1: optional i32 company_id,
    2: optional i32 is_strict,
    3: optional string email_suffix,
    4: optional Timestamp create_time,
    5: optional Timestamp update_time,
    6: optional i32 disable,
    7: optional i32 bd_add_group,
    8: optional i32 bd_use_group_id,
    9: optional i32 auth_mode,
    10:optional string auth_code,
    11:optional string custom,
    12:optional string questions,
    13:optional string custom_hint
}

struct HrEmployeeCustomFieldsDO {
    1: i32 id,
    2: i32 company_id,
    3: string fname,
    4: string fvalues,
    5: i32 forder,
    6: i32 disable,
    7: i32 mandatory,
    8: i32 status
}

struct HrPointsConfDO {
    1:  optional i32 id,
    2:  optional i32 company_id,
    3:  optional string status_name,
    4:  optional i32 reward,
    5:  optional string description
    6:  optional i32 is_using,
    7:  optional i32 order_num
    8:  optional string _update_time,
    9:  optional string tag,
    10: optional i32 is_applier_send,
    11: optional string applier_first,
    12: optional string applier_remark,
    13: optional i32 is_recom_send,
    14: optional string recom_first,
    15: optional string recom_remark,
    16: optional i32 template_id
}

struct HrCompanyDO { 
    1: optional i32 id,
    2: optional i8  type,
    3: optional string name,
    4: optional string introduction,
    5: optional i16 scale,
    6: optional string address,
    7: optional i8 property,
    8: optional string industry,
    9: optional string homepage,
    10: optional string logo,
    11: optional string abbreviation,
    12: optional string impression,
    13: optional string banner,
    14: optional i32 parentId,
    15: optional i32 hraccountId,
    16: optional i32 disable,
    17: optional Timestamp createTime,
    18: optional Timestamp updateTime,
    19: optional i32 source,
    20: optional string slogan
}
