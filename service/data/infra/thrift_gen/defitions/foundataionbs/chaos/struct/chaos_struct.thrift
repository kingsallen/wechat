# file: function.thrift

namespace py thrift_gen.gen.foundation.chaos.struct

/**
 * TODO:list what notation this dateTime represents. eg ISO-8601
 * or if its in the format like YYYY-mm-DD you mentioned.
 */
struct ThirdPartyAccountStruct {
    1: string username,
    2: string password,
    3: string memberName,
    4: i32 remainNum,
    5: string syncTime,
    6: byte channel,
    7: i32 status
}

