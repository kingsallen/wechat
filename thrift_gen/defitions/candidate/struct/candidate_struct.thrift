# file: candidate_struct.thrift

namespace java com.moseeker.thrift.gen.candidate.struct
namespace py thrift_gen.gen.candidate.struct

//推荐人列表接口中的推荐人信息
struct Candidate {
    1:  optional i32 id,                    //candidate_recom_record.id
    2:  optional i32 presenteeUserId,       //被动求职者编号
    3:  optional string presenteeName,      //被动求职者称呼
    4:  optional i32 presenteeFriendId,     //一度朋友编号
    5:  optional string presenteeFriendName,//一度朋友称呼
    6:  optional string presenteeLogo,      //头像
    7:  optional i32 isRecom,               //推荐状态
    8:  optional i32 viewNumber,            //职位查看次数
    9:  optional bool insterested           //是否感兴趣
}

//推荐人列表接口中的推荐人列表
struct CandidateList {
    1:  optional i32 positionId,            //职位编号
    2:  optional string positionName,       //职位名称
    3:  optional list<Candidate> candidates  //职位名称
}

//推荐人列表接口调用参数
struct CandidateListParam {
    1:  optional i32 postUserId,            //推荐者编号 user_user.id
    2:  optional string clickTime,          //点击职位信息的时间
    3:  optional list<i32> recoms,          //是否推荐
    4:  optional i32 companyId              //公司编号
}

struct RecommendResult {
    1: optional i32 id,                     //编号
    2: optional string positionName,        //职位名称
    3: optional string presenteeName,       //浏览者名称
    4: optional bool nextOne,               //是否还有下一个候选人 false：没有，true：还有
    5: optional i32 recomTotal,             //勾选的候选人总数
    6: optional i32 recomIndex,             //推荐的候选人总数
    7: optional i32 recomIgnore             //忽略的候选人人数
}

struct RecommmendParam {
    1: optional i32 id,                     //职位转发推荐记录
    2: optional string realName,            //真实姓名
    3: optional string company,             //公司名称
    4: optional string position,            //职位名称
    5: optional string mobile,              //手机号码
    6: optional string recomReason,         //推荐理由
    7: optional i32 companyId,              //公司编号
    8: optional i32 postUserId,             //推荐人编号
    9: optional string clickTime            //推荐时间
}

struct RecomRecordResult {
    1: optional i32 id,                     //编号
    2: optional string title,               //职位标题
    3: optional string presenteeName,       //浏览者名称
    4: optional string clickTime,           //点击时间
    5: optional i8 recom                    //推荐标识（0 推荐，1 未推荐，2 忽略，3 选中）
}

struct SortResult {
    1: optional i32 count,                  //推荐数量
    2: optional i32 rank,                   //排名
    3: optional i32 hongbao,                //红包金额
}
