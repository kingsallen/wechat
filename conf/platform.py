# coding=utf-8

"""
只适合企业号使用的常量配置

常量使用大写字母，字符串需要时标注为unicode编码
例如 SUCCESS = "成功"
"""
from util.common import ObjectDict

# 企业号搜索页设置

# 栏目设置
# 默认栏目设置

LANDING_SEQ = "1#2#3#4"

LANDING_INDEX_CITY = 1
LANDING_INDEX_SALARY = 2
LANDING_INDEX_OCCUPATION = 3
LANDING_INDEX_DEPARTMENT = 4
LANDING_INDEX_CANDIDATE = 5  # 招聘类型
LANDING_INDEX_EMPLOYMENT = 6  # 工作性质
LANDING_INDEX_DEGREE = 7
LANDING_INDEX_CHILD_COMPANY = 8
LANDING_INDEX_CUSTOM = 9

# 栏目设置
LANDING = ObjectDict({
    LANDING_INDEX_CITY:          {"name": "工作地点", "chpe": "地区", "key": "city"},
    LANDING_INDEX_SALARY:        {"name": "薪资范围", "chpe": "薪资", "key": ["salary_top", "salary_bottom"]},
    LANDING_INDEX_OCCUPATION:    {"name": "职位职能", "chpe": "职能", "key": "occupation"},
    LANDING_INDEX_DEPARTMENT:    {"name": "所属部门", "chpe": "部门", "key": "team_name"},
    LANDING_INDEX_CANDIDATE:     {"name": "招聘类型", "chpe": "类型", "key": "candidate_source_name"},
    LANDING_INDEX_EMPLOYMENT:    {"name": "工作性质", "chpe": "性质", "key": "employment_type_name"},
    LANDING_INDEX_DEGREE:        {"name": "学历要求", "chpe": "学历", "key": "degree_name"},
    LANDING_INDEX_CHILD_COMPANY: {"name": "子公司名称", "chpe": "公司", "key": "publisher_company_id"},
    LANDING_INDEX_CUSTOM:        {"name": "企业自定义字段", "chpe": "自定义", "key": "custom"} #
})


# 薪资范围搜索项
SALARY = ObjectDict({
    "0": {"name": "4k及以下", "salary_bottom": 1, "salary_top": 4},
    "1": {"name": "4k-6k", "salary_bottom": 4, "salary_top": 6},
    "2": {"name": "6k-8k", "salary_bottom": 6, "salary_top": 8},
    "3": {"name": "8k-10k", "salary_bottom": 8, "salary_top": 10},
    "4": {"name": "10k-15k", "salary_bottom": 10, "salary_top": 15},
    "5": {"name": "15k-25k", "salary_bottom": 15, "salary_top": 25},
    "6": {"name": "25k及以上", "salary_bottom": 25, "salary_top": 999},
})

# 学历搜索项
DEGREE = {
    "1": "高中及以下",
    "2": "大专",
    "3": "本科",
    "4": "硕士",
    "5": "MBA",
    "6": "博士",
}

# 媒体类型
MEDIA_TYPE = ('image', 'video')

##########
# 职位列表页设置
POSITION_LIST_PAGE_COUNT = 10

# 职位列表调用基础服务使用的学历查询字符串

SEARCH_DEGREE = ObjectDict({
    "1": "初中,中专,高中,初中及以上,中专及以上,高中及以上",
    "2": "大专,初中及以上,中专及以上,高中及以上,大专及以上",
    "3": "本科,初中及以上,中专及以上,高中及以上,大专及以上,本科及以上",
    "4": "硕士,初中及以上,中专及以上,高中及以上,大专及以上,本科及以上,硕士及以上",
    "5": "MBA,初中及以上,中专及以上,高中及以上,大专及以上,本科及以上,硕士及以上,MBA及以上",
    "6": "博士,初中及以上,中专及以上,高中及以上,大专及以上,本科及以上,硕士及以上,MBA及以上,博士及以上",
})

POSITION_LIST_TITLE_DEFAULT = "我要求职"
POSITION_LIST_TITLE_RECOMLIST = "我要推荐"
