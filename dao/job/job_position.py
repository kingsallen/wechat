# coding=utf-8

# Copyright 2016 MoSeeker

'''
:author 潘煜昕（panyuxin@moseeker.com）
:date 2016.07.25
:table job_position

'''

from dao.base import BaseDao

class JobPositionDao(BaseDao):

    def __init__(self):
        super(JobPositionDao, self).__init__()
        self.table = "job_position"
        self.fields_map = {
            "id": self.constant.TYPE_INT,
            "jobnumber": self.constant.TYPE_STRING, # 职位编号
            "company_id": self.constant.TYPE_INT, # hr_company.id
            "title": self.constant.TYPE_STRING, # 职位标题
            "city": self.constant.TYPE_STRING, # 所在城市
            "department": self.constant.TYPE_STRING, # 所在部门
            "l_jobid": self.constant.TYPE_INT, # jobid from ATS or other channel
            "publish_date": self.constant.TYPE_TIMESTAMP, # 发布时间
            "stop_date": self.constant.TYPE_TIMESTAMP, # 截止日期，为空代表长期有效
            "accountabilities": self.constant.TYPE_STRING, # JD
            "experience": self.constant.TYPE_STRING, # 工作经验
            "requirement": self.constant.TYPE_STRING, # 职位要求
            "language": self.constant.TYPE_STRING, # 语言要求
            "status": self.constant.TYPE_INT, # 0 有效, 1 无效, 2 撤销
            "visitnum": self.constant.TYPE_INT, # 职位访问数
            "source_id": self.constant.TYPE_INT, # 职位来源 0：Moseeker, fk:_job_source.id
            "update_time": self.constant.TYPE_TIMESTAMP, # 更新时间
            "employment_type": self.constant.TYPE_INT, # 0:全职, 1:兼职, 2:合同工, 3:实习生
            "hr_email": self.constant.TYPE_STRING, # HR联系人邮箱，申请通知
            "degree": self.constant.TYPE_INT, # 0:无 1:大专 2:本科 3:硕士 4:MBA 5:博士 6:中专 7:高中 8:博士后 9:初中
            "feature": self.constant.TYPE_STRING, # 职位特色
            "email_notice": self.constant.TYPE_INT, # application after email notice hr, 0:yes 1:no
            "candidate_source": self.constant.TYPE_INT, # 0:社招 1：校招 2:定向招聘
            "occupation": self.constant.TYPE_STRING, # 职位职能
            "is_recom": self.constant.TYPE_INT, # 是否需要推荐0：需要 1：不需要
            "email_resume_conf": self.constant.TYPE_INT, # 0:允许使用email简历进行投递；1:不允许使用email简历投递
            "l_PostingTargetId": self.constant.TYPE_INT, # lumesse每一个职位会生成一个PostingTargetId,用来生成每个职位的投递邮箱地址
            "priority": self.constant.TYPE_INT, # 是否置顶
            "count": self.constant.TYPE_INT, # 添加招聘人数, 0：不限
            "salary_top": self.constant.TYPE_INT, # 薪资上限（k）
            "salary_bottom": self.constant.TYPE_INT, # 薪资下限（k）
            "experience_above": self.constant.TYPE_INT, # 及以上 1：需要， 0：不需要
            "degree_above": self.constant.TYPE_INT, # 及以上 1：需要， 0：不需要
            "management_experience": self.constant.TYPE_INT, # 是否要求管理经验0：需要1：不需要
            "gender": self.constant.TYPE_INT, # 0-> female, 1->male, 2->all
            "share_tpl_id": self.constant.TYPE_INT, # 分享分类0:无1:高大上2：小清新3：逗比
            "publisher": self.constant.TYPE_INT, # 员工ID, sys_employee.id
            "app_cv_config_id": self.constant.TYPE_INT, # 职位开启并配置自定义模板 hr_app_cv_conf.id
            "source": self.constant.TYPE_INT, # 0:手动创建, 1:导入, 9:ATS导入
            "hb_status": self.constant.TYPE_INT, # 是否正参加活动：0=未参加  1=正参加点击红包活动  2=正参加被申请红包活动  3=正参加1+2红包活动
            "age": self.constant.TYPE_INT, # 年龄要求, 0：无要求
            "major_required": self.constant.TYPE_STRING, # 专业要求
            "keyword": self.constant.TYPE_STRING, # 职位关键词
            "reporting_to": self.constant.TYPE_STRING, # 汇报对象
            "is_hiring": self.constant.TYPE_INT, # 是否急招, 1:是 0:否
            "underlings": self.constant.TYPE_STRING, # 下属人数， 0:没有下属
            "target_industry": self.constant.TYPE_INT, # 期望人选所在行业
            "current_status": self.constant.TYPE_INT, # 0:招募中, 1: 未发布, 2:暂停, 3:撤下, 4:关闭
            "position_code": self.constant.TYPE_STRING, # 职能字典code, dict_position.code

            # 以下字段，可以删除
            # "salary": self.constant.TYPE_STRING, # 薪水
            # "job_grade": self.constant.TYPE_INT, # 优先级
            # "lastvisit": self.constant.TYPE_STRING, # openid of last visiter
            # "business_group": self.constant.TYPE_STRING, # 事业群
            # "benefits": self.constant.TYPE_STRING, # 职位福利
            # "hongbao_config_id": self.constant.TYPE_INT, # 红包配置ID
            # "industry": self.constant.TYPE_STRING, # 所属行业
            # "hongbao_config_recom_id": self.constant.TYPE_INT, # 红包配置推荐者ID
            # "hongbao_config_app_id": self.constant.TYPE_INT, # 红包配置申请者ID
            # "hongbao_config_app_id": self.constant.TYPE_INT, # 红包配置申请者ID
            # "province": self.constant.TYPE_STRING, # 所在省
            # "district": self.constant.TYPE_STRING, # 添加区(省市区的区)
            # "child_company_id": self.constant.TYPE_STRING, # hr_child_company.id
            # "language_required": self.constant.TYPE_INT, # 语言要求，1:是 0:否
        }

