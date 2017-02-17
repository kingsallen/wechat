
include "../struct/thirdpart_struct.thrift"
include "../../../common/struct/common_struct.thrift"

namespace com.moseeker.thrift.gen.thirdparty.service

service BindThirdPartServices {
	common_struct.Response sendParamForChaos(1:thirdpart_struct.ThirdPartParamer param);
	common_struct.Response getreMindFromChaos(1:thirdpart_struct.ThirdPartParamer param);
}
