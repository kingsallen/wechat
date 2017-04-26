include "../struct/position_struct.thrift"
include "../../common/struct/common_struct.thrift"
include "../../apps/struct/appbs_struct.thrift"
include "../../dao/struct/dao_struct.thrift"
include "../../dao/struct/campaignrvo_struct.thrift"


namespace java com.moseeker.thrift.gen.position.service
namespace py thrift_gen.gen.position.service
/*
    查询第三方职位职能
*/
service PositionServices {
    common_struct.Response getResources(1:common_struct.CommonQuery query);
    common_struct.Response getRecommendedPositions(1:i32 pid);
    common_struct.Response verifyCustomize(1:i32 positionId);
    // 根据职位Id获取当前职位
    common_struct.Response getPositionById(1:i32 positionId);
    //获取公司两种自定义的字段
    common_struct.Response CustomField(1:string param);
    //转成第三方同步职位数据
    list<position_struct.ThirdPartyPositionForSynchronization> changeToThirdPartyPosition(1:list<appbs_struct.ThirdPartyPosition> form, 2:position_struct.Position position);
    //生成第三方同步职位数据
    position_struct.ThirdPartyPositionForSynchronizationWithAccount createRefreshPosition(1: i32 positionId, 2: i32 channel);
    //是否可以刷新
    bool ifAllowRefresh(1: i32 positionId, 2:i32 channel);
    list<dao_struct.ThirdPartyPositionData> getThirdPartyPositions(1: common_struct.CommonQuery query);

    //微信端职位列表
    list<position_struct.WechatPositionListData> getPositionList(1: position_struct.WechatPositionListQuery query);

    //微信端职位列表的附加红包信息
    list<position_struct.RpExtInfo> getPositionListRpExt(1: list<i32> pids);

    //微信红包职位列表
    list<position_struct.WechatRpPositionListData> getRpPositionList(1: i32 hb_config_id);

    //微信获取红包转发信息
    position_struct.WechatShareData getShareInfo(1: i32 hb_config_id);

    /**Gamma 0.9 接口**/
    // 获取职位列表页头图信息
    campaignrvo_struct.CampaignHeadImageVO headImage();
    // 查询单个职位详情
    position_struct.PositionDetailsVO positionDetails(1:i32 positionId);
}
/*
    查询第三方自定义职能
*/
service PositionDao{
    common_struct.Response getJobCustoms(1:common_struct.CommonQuery query);
    common_struct.Response getJobOccupations(1:common_struct.CommonQuery query);
}
