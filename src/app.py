#!/usr/bin/env python
# coding=utf-8

import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
from tornado.options import options, define

from setting import settings
from route import routes
import utils.session as session
from utils.log import Logger

define("port", default=8000, help="run on the given port", type=int)
define("logpath", default="logs/", help="log path")

tornado.options.parse_command_line()

logger = Logger(logpath=options.logpath)


class Application(tornado.web.Application):

    def __init__(self):
        tornado.web.Application.__init__(self, routes, **settings)

        self.settings = settings
        self.logger = logger

        if settings.get("session"):
            self.session_manager = session.SessionManager(
                settings["session_secret"],
                settings["store_options"],
                settings["session_timeout"])


def main():
    application = Application()
    try:
        logger.info('Enterprise Server Starting, on port : {0}'.format(
            options.port))
        http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()
    except Exception as e:
        logger.error(e)
    finally:
        logger.info('Enterprise Server Closing, on port : {0}'.format(
            options.port))

if __name__ == "__main__":
    main()
