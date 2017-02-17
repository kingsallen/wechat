# coding:UTF-8

from thrift.TTornado import TTornadoStreamTransport
from thrift.protocol import TCompactProtocol
from thrift.protocol import TMultiplexedProtocol

import tornado
from tornado.queues import LifoQueue, QueueEmpty
from tornado.locks import BoundedSemaphore

import traceback


class TMultiplexedCompactProtocolFactory(TCompactProtocol.TCompactProtocolFactory):
    def __init__(self, service_name, *args, **kwargs):
        super(TMultiplexedCompactProtocolFactory, self).__init__(*args, **kwargs)
        self.service_name = service_name

    def getProtocol(self, trans):
        prot = super(TMultiplexedCompactProtocolFactory, self).getProtocol(trans)
        return TMultiplexedProtocol.TMultiplexedProtocol(prot, self.service_name)


class ConnectionPool(object):
    def __init__(self, server_node, client_cls, service_name, conf):
        self.server_node = server_node
        self.client_cls = client_cls
        self.service_name = service_name
        self.conf = conf
        self.pool_size = conf.getint("connection_pool", "size")
        self.connection_queue = LifoQueue(self.pool_size)
        self.semaphore = BoundedSemaphore(self.pool_size)

    @tornado.gen.coroutine
    def get_connection(self):
        i = 1
        yield self.semaphore.acquire()
        try:
            print("get connection: {}".format(self.connection_queue.qsize()))
            conn = yield self.connection_queue.get(timeout=0.1)
            print(conn)
            return conn
        except (QueueEmpty, tornado.gen.TimeoutError):
            try:
                conn = yield self._create_connection()
                return conn
            except Exception as e:
                traceback.print_exc()
                self.semaphore.release()
                raise e
        except Exception as ee:
            traceback.print_exc()
            self.semaphore.release()
            raise ee

    @tornado.gen.coroutine
    def return_connection(self, conn):
        print("try return connection...{}, queue size: {}".format(conn, self.connection_queue.qsize()))
        try:
            yield self.connection_queue.put(conn)
        except Exception as e:
            traceback.print_exc()
            raise e
        print("return connection {}, queue size: {}".format(conn, self.connection_queue.qsize()))
        self.semaphore.release()

    @tornado.gen.coroutine
    def close(self):
        # TODO: add close
        print("_________close connection pool____________start")
        while not self.connection_queue.empty():
            try:
                conn = yield self.connection_queue.get(timeout=0.1)
                try:
                    self._close_connection(conn)
                except:
                    pass
            except QueueEmpty:
                pass
            except Exception as e:
                print(e)
                traceback.print_exc()
        print("_________close connectino pool____________end")

    def _close_connection(self, conn):
        try:
            print("trying to close connection: {}".format(conn))
            conn._transport.close()
            print("success to close connection: {}".format(conn))
        except Exception as e:
            print("fail to close connection: {}".format(conn))
            print(e)
            traceback.print_exc()

    @tornado.gen.coroutine
    def _create_connection(self):
        transport = TTornadoStreamTransport(*self.server_node)
        yield transport.open()
        protocol_family = TMultiplexedCompactProtocolFactory(self.service_name)
        connection = self.client_cls(transport, protocol_family)
        return connection

    def release_connection(self, conn):
        self._close_connection(conn)
        self.semaphore.release()
