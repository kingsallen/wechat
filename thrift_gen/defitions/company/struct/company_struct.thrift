# file: company.struct

namespace java com.moseeker.thrift.gen.company.struct
namespace py thrift_gen.gen.company.struct

typedef string Timestamp;


struct Hrcompany {
   1: optional i32 id,
   2: optional i32 type,
   3: optional string name,
   4: optional string introduction,
   5: optional string scale,
   6: optional string address,
   7: optional i32 property,
   8: optional string industry,
   9: optional string homepage,
   10: optional string logo,
   11: optional string abbreviation,
   12: optional string impression,
   13: optional string banner,
   14: optional i32 parent_id,
   15: optional i32 hraccount_id,
   16: optional i32 disable,
   17: optional Timestamp create_time,
   18: optional Timestamp update_time,
   19: optional i32 source
}

struct CompanyForVerifyEmployee{
    1: optional i32 id,                 //公司编号
    2: optional string name,            //公司名称
    3: optional string abbreviation,    //公司简称
    4: optional string signature        //公司简称
}
