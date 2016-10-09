# coding=utf-8

# Copyright 2016 MoSeeker

"""
系统应用入口 app.py

说明
------------------
* 应用参数初始化
* 应用代理配置
* 启动应用服务

启动系统方式
------------------

shell commond::

    python `pwd`/app.py --port=xxxx --logpath=/path/logs/ &

点我访问 `Moseeker`_.

.. _moseeker: http://localhost:8000
"""

import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
from tornado.options import options

from setting import settings
from route import routes
from utils.common.log import MessageLogger

tornado.options.parse_command_line()
logger = MessageLogger(logpath=options.logpath)


class Application(tornado.web.Application):

    def __init__(self):
        tornado.web.Application.__init__(self, routes, **settings)
        self.settings = settings
        self.logger = logger


def main():
    application = Application()
    try:
        logger.info('Wechat server starting, on port : {0}'.format(options.port))
        http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()
    except Exception as e:
        logger.error(e)
    finally:
        logger.info('Wechat server closing, on port : {0}'.format(options.port))

if __name__ == "__main__":
    main()
