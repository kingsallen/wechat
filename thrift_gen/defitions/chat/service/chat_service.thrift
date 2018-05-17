# file: chat_service.thrift

include "../../common/struct/common_struct.thrift"
include "../struct/chat_struct.thrift"
namespace java com.moseeker.thrift.gen.chat.service
namespace py thrift_gen.gen.chat.service

service ChatService {
    chat_struct.HRChatRoomsVO listHRChatRoom(1: i32 hrId, 2: i32 pageNo, 3: i32 pageSize) throws (1: common_struct.CURDException e)
    chat_struct.HRChatRoomsIndexVO listHRChatRoomByIndex(1: i32 hrId, 2: string keyword, 3: i32 roomId, 4: bool apply, 5: i32 pageSize) throws (1: common_struct.BIZException e)
    chat_struct.UserChatRoomsVO listUserChatRoom(1: i32 userId, 2: i32 pageNo, 3: i32 pageSize) throws (1: common_struct.CURDException e)
    chat_struct.ResultOfSaveRoomVO enterRoom(1: i32 userId, 2: i32 hrId, 3: i32 positionId, 4: i32 roomId, 5: bool is_gamma) throws (1: common_struct.CURDException e)
    void leaveChatRoom(1: i32 roomId, 2: i8 speaker)
    void roleLeaveChatRoom(1: i32 roleId, 2: i8 speaker)

    //列出聊天记录
    chat_struct.ChatsVO listChatLogs(1: i32 roomId, 2: i32 pageNo, 3: i32 pageSize) throws (1: common_struct.CURDException e)
    //保存聊天记录
    i32 saveChat(1: chat_struct.ChatVO chat) throws (1: common_struct.CURDException e)
    //获取聊天记录
    chat_struct.ChatVO getChat(1: i32 roomId, 2: i8 speaker) throws (1: common_struct.CURDException e)
    //获取聊天室最后一条聊天内容
    list<chat_struct.ChatVO> listLastMessage(1: list<i32> roomIdList) throws (1: common_struct.BIZException e)
    //查询聊天室下制定聊天记录之前的历史消息
    chat_struct.ChatHistory listMessage(1: i32 roomId, 2: i32 chatId, 3:i32 pageSize) throws (1: common_struct.BIZException e)
    chat_struct.HRChatRoomVO getChatRoom(1: i32 roomId, 2: i32 hrId) throws (1: common_struct.BIZException e)
    //HR查找用户的结果建议
    list<string> getChatSug(1: i32 hrId, 2: bool applied, 3: string keyword) throws (1: common_struct.BIZException e)
    i32 getHRUnreadCount(1: i32 hrId) throws (1: common_struct.BIZException e)
    //获取聊天室中的hr信息
    chat_struct.HrVO getHrInfo(1: i32 roomId) throws (1: common_struct.BIZException e)
    //更新投递状态
    void updateApplyStatus(1: i32 userId, 2: i32 positionId) throws (1: common_struct.BIZException e)
    //查询语音限制次数
    common_struct.Response pullVoiceFile(1: string serverId) throws (1: common_struct.BIZException e)
    //清零语音限制次数
    common_struct.Response clearVoiceLimitFrequency(1: i32 companyId) throws (1: common_struct.BIZException e)
    //拉取语音文件路径
    common_struct.Response queryVoiceLimitFrequency(1: i32 companyId) throws (1: common_struct.BIZException e)
    //发送报警邮件
    common_struct.Response sendWarnEmail(1: i32 hrId) throws (1: common_struct.BIZException e)
}

