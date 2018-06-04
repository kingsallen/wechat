# file: chat_struct.thrift

namespace java com.moseeker.thrift.gen.chat.struct
namespace py thrift_gen.gen.chat.struct

struct HRChatRoomVO {
    1:  optional i32 id,                    //聊天室编号
    2:  optional i32 userId,                //userdb.user_user.id 用户编号
    3:  optional string name,               //用户名称 userdb.user_user.name > userdb.user_user.nickname
    4:  optional string headImgUrl,         //用户头像 userdb.user_user.headimg > user_wx_user.headimg
    5:  optional string createTime,         //聊天室创建时间
    6:  optional i32 status,                //聊天室状态
    7:  optional i32 unReadNum,             //未读信息数量
    8:  optional bool apply                 //未读信息数量
}

struct HRChatRoomsVO {
    1:  optional i32 pageNo,                //页码
    2:  optional i32 pageSize,              //每页显示的数量
    3:  optional i32 totalPage,             //页数
    4:  optional i32 totalRow,              //聊天室总数
    5:  optional list<HRChatRoomVO> rooms   //HR聊天室信息集合
}

struct HRChatRoomsIndexVO {
    1:  optional i32 userId,                //页码
    2:  optional i32 pageSize,              //每页显示的数量
    3:  optional i32 totalRow,              //聊天室总数
    4:  optional list<HRChatRoomVO> rooms   //HR聊天室信息集合
}

struct UserChatRoomVO {
    1:  optional i32 id,                    //聊天室编号
    2:  optional i32 hrId,                  //userdb.user_hr_account.id HR编号
    3:  optional string name,               //用户名称 userdb.user_user.name > userdb.user_user.nickname
    4:  optional string headImgUrl,         // HR头像 userdb.user_hr_account.headimgurl > user_wx_user.headimgurl > hrdb.hr_company.logo
    5:  optional string companyName,        // 公司名称
    6:  optional string companyLogo,        // 公司logo
    7:  optional string createTime,         //最后一次聊天的时间
    8:  optional i32 status,                //聊天室状态
    9:  optional i32 unReadNum              //未读信息数量
}

struct UserChatRoomsVO {
    1:  optional i32 pageNo,                //页码
    2:  optional i32 pageSize,              //每页显示的数量
    3:  optional i32 totalPage,             //页数
    4:  optional i32 totalRow,              //聊天室总数
    5:  optional list<UserChatRoomVO> rooms   //HR聊天室信息集合
}

struct ChatVO {
    1:  optional string serverId,           //语音文件id，非语音为0
    2:  optional string content,            //聊天内容
    3:  optional i8 speaker,                //0：求职者，1：HR
    4:  optional i8 origin,                 // 0 人工输入，1 欢迎语，2 AI输入
    5:  optional string origin_str,         // 0 人工输入，1 欢迎语，2 AI输入
    6:  optional string msgType,            //消息类型
    7:  optional string assetUrl,           //照片路径
    8:  optional string btnContent,         //按钮信息
    9:  optional i32 roomId,                //聊天室Id
    10: optional i32 positionId             //职位Id
    11: optional i8 duration                //音频时长
	12: optional i32 id                     //聊天记录id
    13: optional string createTime          //创建时间
}

struct ChatHistory {
    1: optional i32 conversationId;         //聊天室编号
    2: optional bool hasMore;               //是否有更多的聊天记录
    3: optional list<ChatVO> chatList;      //聊天列表
    4: optional string hrLeaveTime;         //hr离开聊天室的时间
    5: optional i32 userId;                 // 用户编号
    6: optional string name;                //用户名称
}

struct ChatsVO {
    1:  optional i32 pageNo,                //页码
    2:  optional i32 pageSize,              //每页显示的数量
    3:  optional i32 totalPage,             //页数
    4:  optional i32 totalRow,              //聊天室总数
    5:  optional list<ChatVO> chatLogs        //HR聊天室信息集合
}

struct HrVO {
    1:  optional i32 hrId,                  //HR编号
    2:  optional string hrName,             //HR名称
    3:  optional string hrHeadImg           //HR头像
    4:  optional bool isDelete              //HR是否存在
}

struct UserVO {
    1:  optional i32 userId,                //用户编号
    2:  optional string userName,           //用户名称
    3:  optional string userHeadImg         //用户头像
}

struct PositionVO {
    1:  optional i32 positionId,            //职位编号
    2:  optional string positionTitle,      //职位标题
    3:  optional string companyName,        //公司名称
    4:  optional string city,               //职位的发布地区
    5:  optional i32 salaryTop,             //薪资上限
    6:  optional i32 salaryBottom,          //薪资下限
    7:  optional string updateTime          //职位修改时间
}

struct ResultOfSaveRoomVO {
    1:  optional i32 roomId,                //聊天室ID
    2:  optional bool chatDebut,            //是否是首次聊天 true 首次聊天，false不是首次聊天
    3:  optional PositionVO position,       //职位信息
    4:  optional UserVO user,               //用户信息
    5:  optional HrVO hr                    //HR信息
}
