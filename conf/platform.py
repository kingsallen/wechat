# coding=utf-8

'''
只适合企业号使用的常量配置

常量使用大写字母，字符串需要时标注为unicode编码
例如 SUCCESS = u"成功"

'''

## 企业号搜索页设置

### 栏目设置
### 默认栏目设置

LANDING_SEQ = "1#2#3#4#5#6#7#8#9"

LANDING_INDEX_CITY = 1
LANDING_INDEX_SALARY = 2
LANDING_INDEX_OCCUPATION = 3
LANDING_INDEX_DEPARTMENT = 4
LANDING_INDEX_CANDIDATE = 5 # 招聘类型
LANDING_INDEX_EMPLOYMENT = 6 # 工作性质
LANDING_INDEX_DEGREE = 7
LANGDING_INDEX_CHILD_COMPANY = 8
LANDING_INDEX_CUSTOM = 9

#### 栏目设置
LANDING = {
    LANDING_INDEX_CITY : {"name": u"工作地点", "chpe": u"地区"},
    LANDING_INDEX_SALARY : {"name": u"薪资范围", "chpe": u"薪资"},
    LANDING_INDEX_OCCUPATION : {"name": u"职位职能", "chpe": u"职能"},
    LANDING_INDEX_DEPARTMENT : {"name": u"所属部门", "chpe": u"部门"},
    LANDING_INDEX_CANDIDATE : {"name": u"招聘类型", "chpe": u"类型"},
    LANDING_INDEX_EMPLOYMENT : {"name": u"工作性质", "chpe": u"性质"},
    LANDING_INDEX_DEGREE : {"name": u"学历要求", "chpe": u"学历"},
    LANGDING_INDEX_CHILD_COMPANY : {"name": u"子公司名称", "chpe": u"公司"},
    LANDING_INDEX_CUSTOM : {"name": u"企业自定义字段", "chpe": u"自定义"},
}

#### 薪资范围
SALARY = {
    "0" : {"name": u"4k及以下", "salary_bottom": 0, "salary_top": 4},
    "1" : {"name": u"4k-6k", "salary_bottom": 4, "salary_top": 6},
    "2" : {"name": u"6k-8k", "salary_bottom": 6, "salary_top": 8},
    "3" : {"name": u"8k-10k", "salary_bottom": 8, "salary_top": 10},
    "4" : {"name": u"10k-15k", "salary_bottom": 10, "salary_top": 15},
    "5" : {"name": u"15k-25k", "salary_bottom": 15, "salary_top": 25},
    "6" : {"name": u"25k及以上", "salary_bottom": 25},
}

