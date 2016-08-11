# coding: utf-8

'''
redis session 工具类
'''
import tornado
import tornadis

from setting import settings


class Session(object):

    pool = None

    def __init__(self):

        '''
        Initialize the tornadis
        :return:
        '''

        # if not Session.pool:
        #     tornadis.Client()
        #     Session.pool = tornadis.ClientPool(
        #     dict(port=settings['redis_port'],
        #          host=settings['redis_host'],
        #          connect_timeout=settings['connect_timeout'])
        # )

    @tornado.gen.coroutine
    def put(self, path, bytes, ttl):

        '''
        set a value
        :param path:
        :param bytes:
        :param ttl:
        :return:
        '''

        with (yield Session.pool.connected_client()) as client:
            if ttl:
                yield client.call('SETEX', path, ttl, bytes)
            else:
                yield client.call('SET', path, bytes)

    @tornado.gen.coroutine
    def exists(self, path):

        '''
        judge if the key exists
        :param path:
        :return:
        '''

        with (yield Session.pool.connected_client()) as client:
            exists = yield client.call('EXISTS', path)
            raise tornado.gen.Return(exists)

    @tornado.gen.coroutine
    def remove(self, path):

        '''
        del a key
        :param path:
        :return:
        '''
        with (yield Session.pool.connected_client()) as client:
            yield client.call('DEL', path)

    @tornado.gen.coroutine
    def get(self, path):

        '''
        get a key
        :param path:
        :return:
        '''
        with (yield Session.pool.connected_client()) as client:
            buffer = yield client.call('GET', path)
            raise tornado.gen.Return(buffer)


