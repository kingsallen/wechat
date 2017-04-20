include "../struct/WarnBean.thrift"
namespace java com.moseeker.thrift.gen.warn.service

service WarnSetService{
        void sendOperator(1:WarnBean.WarnBean bean)
}
