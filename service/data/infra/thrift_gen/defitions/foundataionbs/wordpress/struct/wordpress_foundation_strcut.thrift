
namespace py thrift_gen.gen.foundation.wordpress.struct

typedef string Datetime;

struct NewsletterForm {
	1: i32 appid,
	2: i32 account_id,
	3: i8 plateform_type,
	4: i8 return_last_version
}


struct NewsletterData {
	1: i8 show_new_version,
	2: string version,
	3: Datetime update_time,
	4: list<string> update_list,
	5: string url,
	6: string title
}
