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
import tornado.concurrent
import tornado.locale
from tornado.options import options

from setting import settings
import conf.common as constant
from route import platform_routes, qx_routes, help_routes
from handler.common.navmenu import NavMenuModule
from util.common.mq_receiver import RedPacketConsumer

from globals import env, logger, redis, es


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
        self.env = env
        self.redis = redis
        self.es = es
        self.ui_modules.update({
            'NavMenu': NavMenuModule
        })
        self._executor = tornado.concurrent.futures.ThreadPoolExecutor(10)


def make_app():
    """Shared by this module and test as well"""
    app = Application()
    return app


def main():
    application = make_app()
    try:
        logger.info('Wechat server starting on port: {}'.format(options.port))

        tornado.locale.load_translations(settings.locale_path)
        tornado.locale.set_default_locale(settings.default_locale)
        logger.info("Supported locales: {}".format(', '.join(tornado.locale.get_supported_locales())))
        io_loop = tornado.ioloop.IOLoop.instance()
        io_loop.set_blocking_log_threshold(
            settings.blocking_log_threshold)

        http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
        # sc = RedPacketConsumer()
        # application.sc = sc
        # application.sc.connect()
        http_server.listen(options.port)

        io_loop.start()

    except Exception as e:
        logger.error(e)

    finally:
        logger.info('Wechat server closing on port: {0}'.format(options.port))


if __name__ == "__main__":
    main()
