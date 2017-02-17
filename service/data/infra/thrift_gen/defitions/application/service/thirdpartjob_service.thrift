	include "../../thirdpart/struct/thirdpart_struct.thrift"
	include "../../common/struct/common_struct.thrift"
	service OperatorThirdPartService{
		common_struct.Response addPositionToRedis(1:thirdpart_struct.ThirdpartToredis param);
		common_struct.Response updatePositionToRedis(1:thirdpart_struct.ThirdpartToredis param);
	}