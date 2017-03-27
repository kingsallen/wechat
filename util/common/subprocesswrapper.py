# coding=utf-8

# @Time    : 3/22/17 16:17
# @Author  : panda (panyuxin@moseeker.com)
# @File    : subprocess.py
# @DES     :

import time
import subprocess
import tornado.ioloop


class SubProcessWrapper:
    @staticmethod
    def run(cmds, path, callback, command):

        ioloop = tornado.ioloop.IOLoop.instance()
        process = subprocess.Popen(
            cmds,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=path,
            close_fds=True)

        fd = process.stdout.fileno()

        def recv(*args):
            data = process.stdout.readline()
            if data:
                callback(data)
            elif process.poll() is not None:
                ioloop.remove_handler(fd)
                callback(None)
                command()

        def on_timeout():
            try:
                process.kill()
            except:
                pass

        # read handler
        ioloop.add_timeout(time.time() + 5, on_timeout)
        ioloop.add_handler(fd, recv, ioloop.READ)

if __name__ == "__main__":
    def c(a=1):
        print(a)

    def callback_f(arg):
        print("in callback", arg)

    SubProcessWrapper.run('ls', "/Users/panda/Downloads", callback_f ,c)
    tornado.ioloop.IOLoop.instance().start()
