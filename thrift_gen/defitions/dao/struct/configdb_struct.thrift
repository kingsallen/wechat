namespace java com.moseeker.thrift.gen.dao.struct
namespace py thrift_gen.gen.dao.struct.configdb

/**
 * TODO:list what notation this dateTime represents. eg ISO-8601
 * or if its in the format like YYYY-mm-DD you mentioned.
 */
typedef string Timestamp;

struct ConfigSysPointConfTplDO {
    1: optional i32 id,                 //编号 唯一标识
    2: optional string status,          //申请状态
    3: optional i32 award,              //奖励积分
    4: optional string description,     //描述
    5: optional i32 disable,            //是否可用 0 可用 1不可用
    6: optional i32 priority,           //排序
    7: optional i32 typeId,             //多套模板  可能废弃
    8: optional i16 tag,                //interview tag 废弃
    9: optional i32 is_init_award,      //推荐积分初始化 0 需要初始化 1不需要初始化
    10: optional i32 recruitOrder,      //招聘进度顺序
    11: optional string applierView     //求职者文案 可能已经废弃
}
