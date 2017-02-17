# file: function_service.thrift

include "../../../common/struct/common_struct.thrift"
namespace py thrift_gen.gen.function.service

/**
 * TODO:list what notation this dateTime represents. eg ISO-8601
 * or if its in the format like YYYY-mm-DD you mentioned.
 */

service FunctionServices {
    common_struct.Response verifySensitiveWords(1:list<string> contents);
}

