# file: useraccounts.struct

namespace java com.moseeker.thrift.gen.useraccounts.struct
namespace py thrift_gen.gen.useraccounts.struct

typedef string Timestamp;

struct userloginresp {
    1: i32 user_id,
    2: string unionid,
    3: string mobile,
    4: optional Timestamp last_login_time
}

struct userloginreq {
    1: optional string unionid,
    2: optional string mobile,
    3: optional string password
}

