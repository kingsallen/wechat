namespace java com.moseeker.thrift.gen.dao.struct
namespace py thrift_gen.gen.dao.struct.candidatedb

include "../../dao/struct/campaign_head_image_struct.thrift"

// 返回头图信息
struct CampaignHeadImageVO{
    1:i32 status,
    2:campaign_head_image_struct.CampaignHeadImageDO data,
    3:string message
}
