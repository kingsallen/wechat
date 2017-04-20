include "../struct/thirdpart_struct.thrift"
include "../../common/struct/common_struct.thrift"
service OrmThirdPartService{
	common_struct.Response addThirdPartAccount(1:thirdpart_struct.ThirdPartAccount account);
	common_struct.Response updateThirdPartAccount(1:thirdpart_struct.ThirdPartAccount account);
	common_struct.Response addThirdPartPosition(1:thirdpart_struct.ThirdPartPosition position);
	common_struct.Response updateThirdPartPosition(1:thirdpart_struct.ThirdPartPosition position);
	common_struct.Response addThirdPartPositions(1:list<thirdpart_struct.ThirdPartPosition> positions);
	common_struct.Response updateThirdPartPositions(1:list<thirdpart_struct.ThirdPartPosition> positions);
	common_struct.Response getSingleThirdPartAccount(1:i32 companyId);
}
