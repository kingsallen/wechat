namespace py thrift_gen.gen.employee.service

include "../../common/struct/common_struct.thrift"
include "../struct/employee_struct.thrift"

/*
*  员工服务接口
*/
service EmployeeService {
    // 获取用户员工信息
    employee_struct.EmployeeResponse getEmployee(1: i32 userId, 2: i32 companyId);

    // 获取公司员工认证配置信息
    employee_struct.EmployeeVerificationConfResponse getEmployeeVerificationConf(1: i32 companyId);

    // 员工绑定操作
    employee_struct.Result bind(1: employee_struct.BindingParams bindingParams);

    // 员工解绑操作
    employee_struct.Result unbind(1: i32 employeeId, 2: i32 companyId, 3: i32 userId);

    // 获取员工认证自定义字段配置信息
    list<employee_struct.EmployeeCustomFieldsConf> getEmployeeCustomFieldsConf(1: i32 companyId);

    // 员工填写认证自定义字段
    employee_struct.Result setEmployeeCustomInfo(1: i32 employeeId, 2: string customValues);

    // 获取员工积分
    employee_struct.RewardsResponse getEmployeeRewards(1: i32 employeeId, 2: i32 companyId, 3: i32 pageNumber, 4: i32 pageSize);

    // 推荐记录
    list<employee_struct.RecomInfo> getEmployeeRecoms(1: i32 recomId);

    // 员工绑定(邮箱激活)
    employee_struct.Result emailActivation(1: string activationCodee, 2: i32 bindEmailSource);

    // 积分排行榜
    employee_struct.Pagination awardRanking(1: i32 employeeId, 2: i32 companyId, 3: employee_struct.Timespan timespan, 4: i32 pageNum, 5:i32 pageSize) throws (1: common_struct.BIZException e);

    // 员工填写认证自定义字段（更新redis中员工记录）
    employee_struct.Result setCacheEmployeeCustomInfo(1: i32 userId, 2: i32 companyId, 3: string customValues);

    //获取公司内推配置信息
    common_struct.Response getCompanyReferralConf(1:i32 companyId)throws (1: common_struct.BIZException e)
    //插入更新员工点击想要了解内推政策按钮次数
    void updsertCompanyReferralPocily(1:i32 companyId, 2:i32 userId)throws (1: common_struct.BIZException e)
    //计算员工被点赞的数量
    i32 countUpVote(1:i32 employeeId)throws (1: common_struct.BIZException e)
    //计算未查阅的点赞数量
    i32 countRecentUpVote(1:i32 employeeId)throws (1: common_struct.BIZException e)
    //点赞
    i32 upvote(1:i32 employeeId, 2: i32 userId)throws (1: common_struct.BIZException e)
    //取消点赞
    void removeUpvote(1:i32 employeeId, 2:i32 userId)throws (1: common_struct.BIZException e)
    //员工榜单信息
    employee_struct.LeaderBoardInfo fetchLeaderBoardInfo(1:i32 id, 2: i32 type)throws (1: common_struct.BIZException e)
    //最后一名非指定员工的榜单信息
    employee_struct.LeaderBoardInfo fetchLastLeaderBoardInfo(1:i32 id, 2: i32 type)throws (1: common_struct.BIZException e)
    //查找榜单信息
    employee_struct.LeaderBoardType fetchLeaderBoardType(1:i32 companyId)throws (1: common_struct.BIZException e)
    //修改榜单类型
    void updateLeaderBoardType(1:i32 companyId, 2: i8 type)throws (1: common_struct.BIZException e)
    //员工数量
    i32 countEmplyee(1:i32 companyId)throws (1: common_struct.BIZException e)
}

