# 新微信项目
neoweixinrefer项目启动了三个项目：

公众号，聚合号以及招聘助手项目

前端项目：buck_fe

## Getting Started

### 前置准备

1. mkdir workspace
2. cd workspace
3. git clone ssh://git@git.moseeker.com:33897/wechat/wechat.git
4. cd wechat

### 创建依赖环境

1. virtualenv --python=/usr/bin/python3.6 .env
2. source .env/bin/active

### 安装依赖包

1. pip install -r requirement.txt
2. 拷贝内部使用的setting.py（找对接人要）

### 本地运行

- python wechat/app.py

### 运行测试

项目根目录下执行
`make test`

## 代码层次说明

    项目层级目录：
    |--cache    缓存方法
    |----user    用户缓存方法接口
    |----...
    |
    |--conf    常量配置
    |----common.py    系统公用常量
    |----help.py    仟寻招聘助手常量
    |----message.py  消息文案常量
    |----path.py url路径，包括 url，基础服务等
    |----platform.py    企业号常量
    |----qx.py    聚合号常量
    |----wechat.py   wechat 常量
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
    |--oauth   wechat 相关
    |----wechat.py  wechat oauth2.0实现
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
    |--util    工具类
    |----common 公共方法类
    |----tool   工具类
    |----...
    |
    |--.editorconfig
    |--.gitignore    git ignore
    |--.python-version python 版本
    |--app.py    tornado启动类
    |--README.md    README
    |--requirements.txt    项目依赖库
    |--route.py    tornado路由
    |--setting_sample.py    setting配置


## 调用关系

    调用关系：只能向下调用、不能跨级调用、不能向上调用
    handler    路由请求处理；调用pageservice；
                建议一个 handler 对应一个 pageservice，不能调用 dataservice、dao；
                handler之间不能相互调用；
                handler 对应具体功能，遵守 restful 风格
    |||
    pageservice    业务逻辑服务类，主要业务逻辑处理；调用多个dataservice，不能调用handler；pageservice之间不能相互调用
    |||
    dataservice    原子服务类，主要负责与dao进行原子类的处理、轻业务逻辑；一个dao对应一个dataservice，dataservice之间不能相互调用；
    |||
    dao    负责与数据库表结构交互，一张数据表对应一个dao

#### thrift
thrift -r --gen py:tornado xxxxx.thrift

### 编码建议
Python 代码以及风格问题(草稿)：
http://wiki.moseeker.com/python-code-comments.md

## Deployment

- shell 后台运行 

```    
python app.py --port=xxxx --logpath=/path/logs/ & 
```

- supervisorctl 守护进程部署 

```
supervisorctl -c /mnt/xxx

neoweixinrefer_platform:9301 公众号项目
neoweixinrefer_helper:9321 招聘助手项目
neoweixinrefer_qx:9311  聚合号项目

>>start neoweixinrefer_platform:9301
>>stop neoweixinrefer_platform:9301
>>restart neoweixinrefer_platform:9301
```

## Authors

- chendi@moseeker.com
- niuzhenya@moseeker.com
- linjie@moseekr.com
- panlingling@moseeker.com
- yangsongsong@moseeker.com

## License

暂无

## Acknowledgments

暂无
