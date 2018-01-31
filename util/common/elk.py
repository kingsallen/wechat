# coding=utf-8

# @Time    : 9/30/16 16:19
# @Author  : panda (panyuxin@moseeker.com)
# @File    : elk.py
# @DES     : redis 给 elk 系统使用

# Copyright 2016 MoSeeker

import time
import uuid
from abc import ABCMeta, abstractmethod
from collections import deque, namedtuple
from functools import partial
from threading import Thread

import redis
from redis import ConnectionError, TimeoutError
from tornado.options import options
from util.tool import mail_tool
import conf.common as constant
from setting import settings
from multiprocessing import Process


def connect(host, port, timeout, pool_size):
    pool = redis.ConnectionPool(host=host,
                                port=port,
                                max_connections=pool_size)
    redis_client = redis.StrictRedis(connection_pool=pool, socket_timeout=timeout)
    return pool, redis_client


connect_to_cluster = partial(connect,
                             host=settings["elk_cluster"]["redis_host"],
                             port=settings["elk_cluster"]["redis_port"],
                             timeout=settings["elk_cluster"]["redis_socket_timeout"],
                             pool_size=settings["elk_cluster"]["max_connections"])


class IMessageSendable(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def send_message(self, key, value):
        pass


class RedisELK(IMessageSendable):
    # TODO: 加报警邮件
    """A logger implementation sending message to redis server"""

    pool, redis_client = connect_to_cluster()

    _KEY_PREFIX = "log"  # elk只能接受小写的 key

    def __new__(cls, *args):
        if not hasattr(cls, '_instance'):
            orig = super(RedisELK, cls)
            cls._instance = orig.__new__(cls, *args)
        return cls._instance

    def __init__(self, methods=('send_message')):
        self._APPID = constant.APPID[options.env]
        try:
            for method_name in methods:
                assert hasattr(self, method_name)
        except Exception as e:
            print(e)
        self.on = True
        self.guard = Guard(elk_client=self)

    def key_name(self, key):
        return '{0}_{1}_{2}'.format(self._KEY_PREFIX, self._APPID, key)

    def _send_message(self, key, value):
        if value and key:
            key = self.key_name(key)
            self.redis_client.lpush(key, value)
        else:
            pass

    def send_message(self, key, value):
        if self.on:
            try:
                self._send_message(key, value)
            except (ConnectionError, TimeoutError) as e:
                self.guard.handle_error(e)
        else:
            pass

    def switch_to(self, on):
        self.on = on

    @staticmethod
    def reconnect():
        RedisELK.pool.disconnect()
        RedisELK.pool, RedisELK.redis_client = connect_to_cluster()


# Redis错误事件
RedisErrorEvent = namedtuple("RedisErrorEvent", ("timestamp", "exc"))


class Guard:
    """
    ELK守护者
    """
    ERROR_QUEUE_MAX_LENGTH = 3  # 使用一个定长的deque来存储redis_client异常信息
    TIME_SPAN_THRESHOLD_SEC = 10  # 阈值, 多少秒以内出错满多少次, 就算redis错误了, 和ERROR_QUEUE_MAX_LENGTH组合使用
    CHECK_FREQUENCT_SEC = 10  # 客户端认为Redis进入错误状态以后的检查频率

    def __init__(self, elk_client):
        self.elk_client = elk_client
        self.error_queue = deque(maxlen=self.ERROR_QUEUE_MAX_LENGTH)
        self.reset_task = None

    def handle_error(self, e):
        """
        处理一次redis调用异常
        :param e: redis调用的异常信息
        :return: None
        """
        self.error_queue.append(RedisErrorEvent(time.time(), e))
        if self.redis_is_error():
            self.elk_client.switch_to(False)
            self.spawn_reset_task()
            self.send_alert_mail(self.error_queue)
        else:
            pass

    def send_alert_mail(self, error_queue):
        """发生异常时发送报警邮件"""
        email_address = settings['log_guard_warning_email'] or []
        subject = 'log 诊断报警'
        content = error_queue
        Process(
            target=mail_tool.send_mail,
            args=(email_address,
                  subject,
                  content)
        ).start()

    def redis_is_error(self):
        """
        应用程序根据redis的错误反应来判断redis是否挂起了
        """
        if len(self.error_queue) < self.ERROR_QUEUE_MAX_LENGTH:
            return False
        else:
            time_span = self.error_queue[-1].timestamp - self.error_queue[0].timestamp
            return time_span < self.TIME_SPAN_THRESHOLD_SEC

    def reset(self):
        """
        重置
        1. 客户端重连, 如果再次报错则没有后面的2 3两步骤
        2. 重新打开向redis集群push消息
        3. 清空自己的记录错误的队列, 重新开始
        """
        self.elk_client.reconnect()
        self.elk_client.switch_to(True)
        self.error_queue.clear()

    def spawn_reset_task(self):
        """
        分出一个线程来检查redis状态, 回复则reset
        """
        self.reset_task = Thread(target=self.try_reset)
        self.reset_task.start()

    def try_reset(self):
        """
        检测redis的健康状态, 尝试做重新连接
        :return:
        """
        while True:
            try:
                good = self.check_redis_healthy_status()
                if not good:
                    time.sleep(self.CHECK_FREQUENCT_SEC)
                    continue
                else:
                    self.reset()
                    self.reset_task = None
                    break  # to end the thread
            except:
                time.sleep(self.CHECK_FREQUENCT_SEC)  #

    @staticmethod
    def check_redis_healthy_status():
        """
        检查redis的健康状态
        以后可以增强判断标准, 什么才是好的, 什么才是坏的
        :return: bool
        """
        try:
            pool, redis_client = connect_to_cluster(pool_size=1)
            k = "check_redis_healthy_status:{}".format(uuid.uuid1())
            redis_client.setex(k, 100, "")  # 这个100是随便写的, 为了保证最终这个塞进去的key能消失掉
            redis_client.delete(k)
        except:
            return False
        else:
            return True
        finally:
            pool.disconnect()
