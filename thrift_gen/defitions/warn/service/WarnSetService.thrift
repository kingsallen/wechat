include "../struct/WarnBean.thrift"
namespace py thrift_gen.gen.warn.service

service WarnSetService{
        void sendOperator(1:WarnBean.WarnBean bean)
}
