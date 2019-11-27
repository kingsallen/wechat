import pika
from pika import TornadoConnection
import json
from globals import logger

import conf.common as const
from setting import settings
from service.page.redpacket.redpacket import RedpacketPageService


class Consumer(object):
    """ The pika client the tornado will be part of """

    def __init__(self):
        logger.debug('PikaClient: __init__')
        self.connecting = False
        self.connection = None
        self.channel = None
        self.event_listeners = {}
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
        return TornadoConnection(param, on_open_callback=self.on_connected)

    def on_connected(self, connection):
        logger.debug('PikaClient: connected to RabbitMQ')
        self.connection = connection
        self.connection.add_on_close_callback(self.on_closed)
        self.connection.channel(self.on_channel_open)

    def on_closed(self, connection, reply_code, reply_text):
        logger.warning('PikaClient: rabbit connection closed, reopening in 1 seconds: (%s) %s', reply_code, reply_text)
        self.connection.add_timeout(1, self.reconnect)

    def reconnect(self):
        self.connection = self.connect()

    def on_channel_open(self, channel):
        logger.info('PikaClient: Channel open, Declaring exchange {}'.format(const.REDPACKET_EXCHANGE))
        self.channel = channel
        # declare exchanges, which in turn, declare
        # queues, and bind exchange to queues
        self.channel.exchange_declare(
            self.on_exchange_declareok,
            exchange=const.REDPACKET_EXCHANGE,
            type=const.EXCHANGE_TYPE,
            durable=const.DURABLE)

    def on_exchange_declareok(self, unused_frame):
        logger.debug('Exchange declared')


class RedPacketConsumer(Consumer):

    def on_exchange_declareok(self, unused_frame):
        logger.debug('Exchange declared')
        logger.info('Declaring queue %s' % const.REDPACKET_QUEUE)
        self.channel.queue_declare(self.on_queue_declare, queue=const.REDPACKET_QUEUE, durable=const.DURABLE)

    def on_queue_declare(self, result):
        self.channel.queue_bind(
            self.on_queue_bind,
            exchange=const.REDPACKET_EXCHANGE,
            queue=const.REDPACKET_QUEUE,
            routing_key=const.MQ_REDPACKET_ROUTING_KEY)

    def on_queue_bind(self, is_ok):
        logger.debug('PikaClient: Exchanges and queue created/joined')
        self.channel.basic_consume(self.on_message, queue=const.REDPACKET_QUEUE)

    def on_message(self, channel, basic_deliver, properties, body):
        try:
            logger.debug('PikaClient: Received message # %s from %s: %s' % (basic_deliver.delivery_tag, properties.app_id, body))
            # important, since rmq needs to know that this msg is received by the
            # consumer. Otherwise, it will be overwhelmed
            data = json.loads(str(body, encoding="utf-8"))
            data['rp_type'] = basic_deliver.routing_key.split('.')[0]
            self.redpacket_ps.handle_red_packet_from_rabbitmq(data)
        except Exception as e:
            logger.error("PikaClient: handle message error:{}".format(e))
            self.channel.add_on_close_callback(self.on_channel_closed)
        channel.basic_ack(delivery_tag=basic_deliver.delivery_tag)

    def on_channel_closed(self, channel, reply_code, reply_text):
        logger.warning('Channel closed, reopening in 1 seconds: (%s) %s',
                       reply_code, reply_text)
        self.channel.close()





