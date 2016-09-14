# 新微信项目

Python 代码以及风格问题(草稿)：
http://wiki.moseeker.com/python-code-comments.md

## 代码层次说明

    项目层级目录：
    |--cache    缓存方法
    |----user    用户缓存方法接口
    |----...
    |
    |--conf    常量配置
    |----common    系统公用常量
    |----help    仟寻招聘助手常量
    |----platform    企业号常量
    |----qx    聚合号常量
    |
    |--dao   模型，针对单个表结构申明字段和类型，按DB分文件夹
    |----hr    hrdb相关数据表结构
    |----job    jobdb职位相关表结构
    |----base.py    封装数据库查询公共方法
    |----...
    |
    |--handler    用户请求处理，接受路由请求，轻逻辑
    |----common    公共请求方法
    |----help    仟寻招聘助手
    |----platform    企业号
    |----qx    聚合号
    |----base.py    请求方法父类，封装公共类
    |
    |--logs    请求日志
    |
    |--service    服务类，主要处理业务逻辑
    |----data    dataservice,主要与dao进行交互，提供原子性的方法，按DB分包
    |------hr    hrdb相关类
    |------job    jobdb职位相关类
    |------base.py    dao的声明
    |------...
    |----page    dataservice，主要与dataservice、handler交互，处理主要的业务逻辑
    |------common    公共方法类
    |------hr    HR相关业务逻辑类
    |------job    职位相关业务逻辑类
    |------base.py    dataservice的声明
    |------...
    |
    |--template    模板
    |
    |--tests  单元测试
    |
    |--utils    工具类
    |----common 公共方法类
    |----tool   工具类
    |
    |--.editorconfig
    |--.gitignore    git ignore
    |--app.py    tornado启动类
    |--README.md    README
    |--requirements.txt    项目依赖库
    |--route.py    tornado路由
    |--setting_sample.py    setting配置


## 调用关系

    调用关系：只能向下调用、不能跨级调用、不能向上调用
    handler    路由请求处理；调用pageservice；建议一个 handler 对应一个 pageservice，不能调用 dataservice、dao；handler之间不能相互调用
    |||
    pageservice    业务逻辑服务类，主要业务逻辑处理；调用多个dataservice，不能调用handler；pageservice之间不能相互调用
    |||
    dataservice    原子服务类，主要负责与dao进行原子类的处理、轻业务逻辑；一个dao对应一个dataservice，dataservice之间不能相互调用；
    |||
    dao    负责与数据库表结构交互，一张数据表对应一个dao
