# file: candidate_service.thrift

include "../../common/struct/common_struct.thrift"

namespace java com.moseeker.thrift.gen.candidate.service
namespace py thrift_gen.gen.candidate.service

service CandidateService {
    void glancePosition(1:i32 userId, 2:i32 positionId, 3:i32 shareChainId);

    // 感兴趣职位
    common_struct.Response changeInteresting(1: i32 user_id, 2: i32 position_id, 3: i8 is_interested);
}

