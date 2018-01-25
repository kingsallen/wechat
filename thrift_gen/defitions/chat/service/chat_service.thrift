# file: chat_service.thrift

include "../../common/struct/common_struct.thrift"
include "../struct/chat_struct.thrift"
namespace java com.moseeker.thrift.gen.chat.service
namespace py thrift_gen.gen.chat.service

service ChatService {
    chat_struct.HRChatRoomsVO listHRChatRoom(1: i32 hrId, 2: i32 pageNo, 3: i32 pageSize) throws (1: common_struct.CURDException e)
    chat_struct.UserChatRoomsVO listUserChatRoom(1: i32 userId, 2: i32 pageNo, 3: i32 pageSize) throws (1: common_struct.CURDException e)
    chat_struct.ResultOfSaveRoomVO enterRoom(1: i32 userId, 2: i32 hrId, 3: i32 positionId, 4: i32 roomId, 5: bool is_gamma) throws (1: common_struct.CURDException e)
    void leaveChatRoom(1: i32 roomId, 2: i8 speaker)

    //列出聊天记录
    chat_struct.ChatsVO listChatLogs(1: i32 roomId, 2: i32 pageNo, 3: i32 pageSize) throws (1: common_struct.CURDException e)
    //保存聊天记录
    i32 saveChat(1: chat_struct.ChatVO chat) throws (1: common_struct.CURDException e)
    //获取聊天记录
    chat_struct.ChatVO getChat(1: i32 roomId, 2: i8 speaker) throws (1: common_struct.CURDException e)
}
