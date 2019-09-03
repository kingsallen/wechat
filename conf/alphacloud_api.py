# coding=utf-8
from util.tool.dict_tool import ObjectDict


"""临时写法，请勿再使用这种写法，写到conf/newinfra_service_conf/service_info.py中"""
redpacket_service = ObjectDict({
    "service": ObjectDict({
        "appid": "A11039",
        "interfaceid": "A11039001",
        "service_name": "redpacket"
    }),
    "api": ObjectDict(CLOUD_REDPACKET_SCENE="/v4/redpacket/scene",
                      CLOUD_REDPACKET_CLAIM="/v4/redpacket/open-redpacket",
                      CLOUD_USER_REDPACKET_LIST="/v4/redpackets",
                      CLOUD_POSITION_LIST_RP_EXT="/v4/activity-position/positions",
                      CLOUD_RP_POSITION_LIST_SHARE_INFO='/v4/activity/share-info',
                      CLOUD_RP_POSITION_SHARE_INFO='/v4/activity-position/position-scene')

})
