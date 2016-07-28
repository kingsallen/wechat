# coding=utf-8

'''
只适合企业号使用的常量配置
'''

## 企业号搜索页设置

### 栏目设置
### 默认栏目设置
landing_seq = "1#2#3#4#5#6#7#8#9"

landing_index_city = 1
landing_index_salary = 2
landing_index_occupation = 3
landing_index_department = 4
landing_index_candidate = 5 # 招聘类型
landing_index_employment = 6 # 工作性质
landing_index_degree = 7
landing_index_child_company = 8
landing_index_custom = 9

landing = {
    landing_index_city : {"name": "工作地点", "chpe": "地区", "priority": 1},
    landing_index_salary : {"name": "薪资范围", "chpe": "薪资", "priority": 2},
    landing_index_occupation : {"name": "职位职能", "chpe": "职能", "priority": 3},
    landing_index_department : {"name": "所属部门", "chpe": "部门", "priority": 4},
    landing_index_candidate : {"name": "招聘类型", "chpe": "类型", "priority": 5},
    landing_index_employment : {"name": "工作性质", "chpe": "性质", "priority": 6},
    landing_index_degree : {"name": "学历要求", "chpe": "学历", "priority": 7},
    landing_index_child_company : {"name": "子公司名称", "chpe": "公司", "priority": 8},
    landing_index_custom : {"name": "企业自定义字段", "chpe": "自定义", "priority": 9},
}

salary = {
    "0" : {"name": "4k及以下", "salary_bottom": 0, "salary_top": 4},
    "1" : {"name": "4k-6k", "salary_bottom": 4, "salary_top": 6},
    "2" : {"name": "6k-8k", "salary_bottom": 6, "salary_top": 8},
    "3" : {"name": "8k-10k", "salary_bottom": 8, "salary_top": 10},
    "4" : {"name": "10k-15k", "salary_bottom": 10, "salary_top": 15},
    "5" : {"name": "15k-25k", "salary_bottom": 15, "salary_top": 25},
    "6" : {"name": "25k及以上", "salary_bottom": 25},
}

