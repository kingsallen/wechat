
namespace py thrift_gen.gen.foundation.hraccount.struct

typedef string Datetime;
struct ThirdPartAccount{
	1: i32 id,
	2: string name,
	3: i32 channel,
	4: string username,
	5: string password,
	6: string membername,
	7: i32 binding,
	8: i32 company_id,
	9: i32 remain_num,
	10: Datetime sync_time
}
struct ThirdPartPosition{
	1: i32 id,
	2: i32 position_id,
	3: string third_part_position_id,
	4: i32 channel,
	5: i32 is_synchronization,
	6: i32 is_refresh,
	7: Datetime sync_time,
	8: string occupation
}
struct ThirdPartParamer{
	1: i32 appid,
	2: i32 user_id,
	3: i32 company_id,
	4: string username,
	5: string password,
	6: string member_name,
	7: i32 channel
}
struct ThirdpartToredis{
	1: optional string params,
	2:i32 user_id,
	3:i32 company_id,
	4:i32 appid,
	5:optional string positions
}
