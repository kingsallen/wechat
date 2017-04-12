# file: common.struct

namespace java com.moseeker.thrift.gen.common.struct
namespace py thrift_gen.gen.common.struct

struct Response {
    1: i32 status,
    2: string message,
    3: optional string data
}

struct CommonQuery {
    1: i32 appid,
    2: optional i32 page,
    3: optional i32 per_page,
    4: optional string sortby,
    5: optional string order,
    6: optional string fields,
    7: optional bool nocache=false,
    8: optional map<string, string> equalFilter,
    9: optional list<string> attributes,
    10: optional list<string> grouops
}

exception CURDException {
    1: i32 code,
    2: string message
}

exception BIZException {
    1: i32 code,
    2: string message
}
