import pika
from pika import TornadoConnection
import json
from globals import logger

import conf.common as const
from setting import settings
from service.page.redpacket.redpacket import RedpacketPageService


class ScreenRedPacketConsumer(object):
    """ The pika client the tornado will be part of """

    def __init__(self, io_loop):
        print('PikaClient: __init__')
        self.io_loop = io_loop
        self.connected = False
        self.connecting = False
        self.connection = None
        self.channel = None
        self.event_listeners = {}
        self.redpacket_ps = RedpacketPageService()

    def connect(self):
        """ Connect to the broker """
        if self.connecting:
            logger.debug('PikaClient: Already connecting to RabbitMQ')
            return

        print('PikaClient: Connecting to RabbitMQ')
        self.connecting = True

        cred = pika.PlainCredentials(settings['rabbitmq_username'], settings['rabbitmq_password'])
        param = pika.ConnectionParameters(
            host=settings['rabbitmq_host'],
            port=settings['rabbitmq_port'],
            connection_attempts=settings['rabbitmq_connection_attempts'],
            heartbeat_interval=settings['rabbitmq_heartbeat_interval'],
            credentials=cred)
        self.connection = TornadoConnection(
            param,
            on_open_callback=self.on_connected)
        self.connection.add_on_close_callback(self.on_closed)

    def on_connected(self, connection):
        logger.debug('PikaClient: connected to RabbitMQ')
        self.connected = True
        self.connection = connection
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        logger.debug('PikaClient: Channel open, Declaring exchange')
        self.channel = channel
        # declare exchanges, which in turn, declare
        # queues, and bind exchange to queues
        self.channel.exchange_declare(
            exchange='someexchange',
            type='topic')
        self.channel.queue_declare(self.on_queue_declare, exclusive=True)

    def on_queue_declare(self, result):
        queue_name = result.method.queue
        self.channel.queue_bind(
            self.on_queue_bind,
            exchange='someexchange',
            queue=queue_name,
            routing_key='commands.*')
        self.channel.basic_consume(self.on_message)

    def on_queue_bind(self, is_ok):
        logger.debug('PikaClient: Exchanges and queue created/joined')

    def on_closed(self, connection):
        logger.debug('PikaClient: rabbit connection closed')
        self.io_loop.stop()

    def on_message(self, channel, method, header, body):
        logger.debug('PikaClient: message received: %s' % body)
        self.notify_listeners(body)
        # important, since rmq needs to know that this msg is received by the
        # consumer. Otherwise, it will be overwhelmed
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def notify_listeners(self, event_obj):
        # do whatever you wish
        pass

    def add_event_listener(self, listener):
        # listener.id is the box id now
        self.event_listeners[listener.id] = {
            'id': listener.id, 'obj': listener}
        logger.debug('PikaClient: listener %s added' % repr(listener))

    def remove_event_listener(self, listener):
        try:
            del self.event_listeners[listener.id]
            logger.debug('PikaClient: listener %s removed' % repr(listener))
        except KeyError:
            pass

    def event_listener(self, some_id):
        """ Gives the socket object with the given some_id """

        tmp_obj = self.event_listeners.get(some_id)
        if tmp_obj is not None:
            return tmp_obj['obj']
        return None







