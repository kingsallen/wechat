# coding=utf-8

# @Time    : 3/22/17 16:17
# @Author  : panda (panyuxin@moseeker.com)
# @File    : subprocess.py
# @DES     :

import time
import subprocess
import tornado.ioloop

class Sub:
    def subprocess(self, cmd, path, callback, command):

        ioloop = tornado.ioloop.IOLoop.instance()
        PIPE = subprocess.PIPE
        pipe = subprocess.Popen(
            cmd, shell=True, stdin=PIPE, stdout=PIPE,
            stderr=subprocess.STDOUT, cwd=path, close_fds=True)
        fd = pipe.stdout.fileno()

        def recv(*args):
            data = pipe.stdout.readline()
            if data:
                callback(data)
            elif pipe.poll() is not None:
                ioloop.remove_handler(fd)
                callback(None)

                command()

        def on_timeout():
            try:
                pipe.kill()
            except:
                pass

        # read handler
        ioloop.add_timeout(time.time() + 5, on_timeout)
        ioloop.add_handler(fd, recv, ioloop.READ)

if __name__ == "__main__":

    cmd = "ls"
    def c():
        print (1)

    Sub.subprocess(cmd, "aa", "f", c)
