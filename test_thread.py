# encoding=utf-8

import threading
import time


class T(threading.Thread):
    def __init__(self, name):
        super(T, self).__init__()
        self.setName(name)

    def run(self):
        for i in range(10):
            print("%s - %s" % (self.getName(), i))
            time.sleep(0.1)
            if self.getName() == 't1':
                t2.join()

var = 0

class IncreThread(threading.Thread):
    def run(self):
        global var
        print('before,var is %s', var)
        lock.acquire()
        var += 1
        lock.release()
        print('after,var is %s', var)

lock = threading.Lock()

def use_incre_thread():
    threads = []
    for i in range(50):
        t = IncreThread()
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print('After 10 times,var is %s', var)

if __name__ == '__main__':

        use_incre_thread()
    # t1 = T("t1")
    # t2 = T("t2")
    # t1.start()
    # t2.start()
    #
    # t1.join()
