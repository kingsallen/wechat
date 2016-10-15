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
import conf.common as constant
import conf.platform as plat_constant
import conf.qx as qx_constant
import conf.help as help_constant
import conf.wechat as wx_constant

from route import platform_routes, qx_routes, help_routes
from util.common.log import MessageLogger
from util.common.cache import BaseRedis

tornado.options.parse_command_line()
logger = MessageLogger(logpath=options.logpath)
redis = BaseRedis()


class Application(tornado.web.Application):

    def __init__(self):
        # 选择加载的 routes
        if options.env == constant.ENV_PLATFORM:
            tornado.web.Application.__init__(self, platform_routes, **settings)
        elif options.env == constant.ENV_QX:
            tornado.web.Application.__init__(self, qx_routes, **settings)
        else:
            tornado.web.Application.__init__(self, help_routes, **settings)

        self.settings = settings
        self.logger = logger
        self.env = options.env
        self.constant = constant
        self.plat_constant = plat_constant
        self.qx_constant = qx_constant
        self.help_constant = help_constant
        self.wx_constant = wx_constant
        self.redis = redis


def main():
    application = Application()
    try:
        logger.info('Wechat server starting on port: {0}'.format(options.port))
        http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
        http_server.listen(options.port)

        tornado.ioloop.IOLoop.instance().set_blocking_log_threshold(
            settings['blocking_log_threshold'])
        tornado.ioloop.IOLoop.instance().start()
    except Exception as e:
        logger.error(e)
    finally:
        logger.info('Wechat server closing on port: {0}'.format(options.port))

if __name__ == "__main__":

    main()
