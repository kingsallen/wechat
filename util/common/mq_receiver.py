import pika
from pika import TornadoConnection
import json
from globals import logger

import conf.common as const
from setting import settings
from service.page.redpacket.redpacket import RedpacketPageService


class Consumer(object):
    """ The pika client the tornado will be part of """
    # todo 因为没有消费端的需求，因此这个消费者没写完，没有做过测试，请不要直接拿来用。
    # todo 在ioloop.start()的时候通过connect()方法把所有的消费者都启动（未完成）
    def __init__(self, exchange, exchange_type, routing_key="", queue="", durable=True):
        """ Create a new instance of the consumer class.

        :param exchange: exchange 名
        :param exchange_type: exchange 类型
        :param routing_key: 默认路由键
        :param queue: queue 名，允许为空
        :param durable: 2: 消息持久化
        """
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.routing_key = routing_key
        self.queue = queue

        # 默认消息持久化
        self.durable = durable

        self.connection = None
        self.channel = None
        self.redpacket_ps = RedpacketPageService()

    def connect(self):
        """ Connect to the broker """
        logger.info("Connecting to {}".format(settings['rabbitmq_host']))

        cred = pika.PlainCredentials(settings['rabbitmq_username'], settings['rabbitmq_password'])
        param = pika.ConnectionParameters(
            host=settings['rabbitmq_host'],
            port=settings['rabbitmq_port'],
            connection_attempts=settings['rabbitmq_connection_attempts'],
            heartbeat_interval=settings['rabbitmq_heartbeat_interval'],
            credentials=cred)
        return TornadoConnection(param, on_open_callback=self.on_connected, on_close_callback=self.on_channel_closed)

    def on_connected(self, connection):
        logger.debug('PikaClient Consumer: connected to RabbitMQ')
        self.connection = connection
        self.connection.add_on_close_callback(self.on_closed)
        self.connection.channel(self.on_channel_open)

    def on_closed(self, connection, reply_code, reply_text):
        logger.warning('PikaClient Consumer: rabbit connection closed, reopening in 1 seconds: (%s) %s', reply_code, reply_text)
        self.connection.add_timeout(1, self.reconnect)

    def reconnect(self):
        self.connection = self.connect()

    def on_channel_open(self, channel):
        logger.info('PikaClient Consumer: Channel open, Declaring exchange {}'.format(const.REDPACKET_EXCHANGE))
        self.channel = channel
        # declare exchanges, which in turn, declare
        # queues, and bind exchange to queues
        self.channel.exchange_declare(
            self.on_exchange_declareok,
            exchange=self.exchange,
            type=self.exchange_type,
            durable=self.durable)

    def on_exchange_declareok(self, unused_frame):
        logger.debug('Consumer Exchange declared')
        logger.info('Consumer Declaring queue %s' % unused_frame)
        self.channel.queue_declare(self.on_queue_declare, queue=self.queue, durable=self.durable)

    def on_queue_declare(self, result):
        self.channel.queue_bind(
            self.on_queue_bind,
            exchange=self.exchange,
            queue=self.queue,
            routing_key=self.routing_key)

    def on_queue_bind(self, is_ok):
        logger.debug('PikaClient Consumer: Exchanges and queue created/joined')
        self.channel.basic_consume(self.on_message, queue=self.queue)

    def on_message(self, channel, basic_deliver, properties, body):
        """Do what do you want to do"""
        pass
        channel.basic_ack(delivery_tag=basic_deliver.delivery_tag)

    def on_channel_closed(self, channel, reply_code, reply_text):
        logger.warning('Consumer Channel closed, reopening in 1 seconds: (%s) %s',
                       reply_code, reply_text)
        # self.channel.close()


# todo 以下仅为思路，请完善下列代码


# 具体的消费者
class RedPacketConsumer(Consumer):

    def __init__(self, *args, **kwargs):
        # todo 补充属性（具体的exchange等）
        super(RedPacketConsumer, self).__init__(*args, **kwargs)

    def on_message(self, channel, basic_deliver, properties, body):
        try:
            logger.debug('PikaClient Consumer: Received message # %s from %s: %s' % (basic_deliver.delivery_tag, properties.app_id, body))
            # important, since rmq needs to know that this msg is received by the
            # consumer. Otherwise, it will be overwhelmed
            data = json.loads(str(body, encoding="utf-8"))
            data['rp_type'] = basic_deliver.routing_key.split('.')[0]
            self.redpacket_ps.handle_red_packet_from_rabbitmq(data)
        except Exception as e:
            logger.error("PikaClient Consumer: handle message error:{}".format(e))
        channel.basic_ack(delivery_tag=basic_deliver.delivery_tag)


consumer_list = []
redpacket_consumer = RedPacketConsumer(exchange=1)  # 传入属性
consumer_list.append(redpacket_consumer)


# todo ioloop启动的时候，启动所有的消费者
def connect():
    for c in consumer_list:
        c.connect()




