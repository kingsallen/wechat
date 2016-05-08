# 微信端重构项目

## Python 代码以及风格问题(草稿)：

1. 禁止使用 mutable 的 default 参数，比如：[], {}。原因以及处理方法：http://docs.python-guide.org/en/latest/writing/gotchas/
2. 使用 flake8 linter（含 pep 8）
3. 使用兼容 python 3 的语法（pycharm 开启 inspection）
4. 变量名采取下划线分割规范，不要和驼峰混用
5. 禁止在 master 分支存在被注释的代码
6. 禁止 `reload(sys);sys.setdefaultencoding('utf-8')`
7. 用 tornado.util.ObjectDict 替代 mdict
8. 业务代码文本优先使用 unicode 类型
