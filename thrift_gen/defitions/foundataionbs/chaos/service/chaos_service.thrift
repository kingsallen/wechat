# file: function_service.thrift

include "../../../common/struct/common_struct.thrift"
include "../struct/chaos_struct.thrift"
include "../../../position/struct/position_struct.thrift"

namespace java com.moseeker.thrift.gen.foundation.chaos.service
namespace py thrift_gen.gen.foundation.chaos.service


/**
 * TODO:list what notation this dateTime represents. eg ISO-8601
 * or if its in the format like YYYY-mm-DD you mentioned.
 */

service ChaosServices {
    //绑定第三方帐号
    common_struct.Response binding(1:string username, 2:string password, 3:string member_name, 4:byte channel);
    //同步可发布职位数
    chaos_struct.ThirdPartyAccountStruct synchronization(1:chaos_struct.ThirdPartyAccountStruct thirdPartyAccount);
    //同步职位
    common_struct.Response synchronizePosition(1:list<position_struct.ThirdPartyPositionForSynchronizationWithAccount> positions);
    //刷新职位
    common_struct.Response refreshPosition(1:position_struct.ThirdPartyPositionForSynchronizationWithAccount position);
}

