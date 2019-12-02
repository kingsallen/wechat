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

import time
import signal
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.concurrent
import tornado.locale
from functools import partial
from tornado.options import options

from setting import settings
import conf.common as constant
from route import platform_routes, qx_routes, help_routes
from handler.common.navmenu import NavMenuModule

from globals import env, logger, redis, es, sa


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
        self.sa = sa
        self.ui_modules.update({
            'NavMenu': NavMenuModule
        })
        self._executor = tornado.concurrent.futures.ThreadPoolExecutor(10)


def make_app():
    """Shared by this module and test as well"""
    app = Application()
    return app


def sig_handler(sig, frame, sensors_sa, server):
    """信号处理函数
    """
    logger.info('HR Server  sig handler ...')
    tornado.ioloop.IOLoop.instance().add_callback(partial(shutdown, sensors_sa=sensors_sa, server=server))


def shutdown(sensors_sa, server):
    """进程关闭处理
    """
    # 停止接受Client连接
    logger.info('HR Server Shutdown ...')
    sensors_sa.close()
    logger.info('HR Server sensors sa in Shutdown ...')
    server.stop()

    io_loop = tornado.ioloop.IOLoop.instance()
    deadline = time.time() + settings.get('hold_on_for_requests_seconds', 10)  # 设置最长强制结束时间

    def stop_loop():
        now = time.time()
        if now < deadline:
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()

    stop_loop()


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

        signal_handler = partial(sig_handler,
                                 sensors_sa=sa,
                                 server=http_server
                                 )

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        http_server.listen(options.port)

        io_loop.start()

    except Exception as e:
        logger.error(e)

    finally:
        sa.flush()
        logger.info('Wechat server closing on port: {0}'.format(options.port))


if __name__ == "__main__":
    main()
