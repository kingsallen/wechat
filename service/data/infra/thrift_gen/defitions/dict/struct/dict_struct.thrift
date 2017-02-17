namespace py thrift_gen.gen.dict.struct

typedef string Timestamp;

/*
  城市字典实体
*/
struct City {
    1: optional i32 code,
    2: optional string name,
    3: optional i8 level,
    4: optional i8 hot_city, // 热门城市 0:否 1：是
    5: optional string ename, // 英文名称
    6: optional i8 is_using // 正在使用 0:没在用 1:在使用
}

/*
 *第三方渠道城市
 */
struct CityMap {
    1: i32 id,
    2: i32 code,
    3: i32 code_other,
    4: i32 channel,
    5: i32 status,
    6: string create_time
}

/*
  院校字典实体
*/
struct College {
    1: optional i32 college_code,
    2: optional string collge_name,
    3: optional string collge_logo,
    4: optional i32 province_code, // 所在地 code
    5: optional string province_name // 所在地 名称
}

/*
   国家字典实体
*/
struct DictCountry {
    1: optional i32 id,
    2: optional string name,
    3: optional string ename,
    4: optional string iso_code_2,
    5: optional string iso_code_3,
    6: optional string code,
    7: optional string icon_class,
    8: optional i8 hot_country,
    9: optional i32 continent_code
}

/*
  常量字典实体
*/
struct DictConstant {
    1: optional i32 code,                // 常量code
    2: optional string name,             // 常量名称
    3: optional i32 priority,            // 优先级
    4: optional i32 parent_code,         // 常量类型
    5: optional Timestamp create_time,   // 表记录创建时间
    6: optional Timestamp update_time    // 最新更新时间
}

/*
  行业
*/
struct IndustryConstant {
    1: optional i32 code,                // 常量code
    2: optional string name,             // 常量名称
    3: optional i32 type		 // 字典分类
}
