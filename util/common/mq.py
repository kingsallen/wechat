# coding=utf-8

import pika
import json
from globals import logger

import conf.common as const
from setting import settings


class MQPublisher(object):



    def __init__(self, amqp_url, exchange, exchange_type, routing_key, appid,
                 queue='', delivery_mode=2):
        """ Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        :param amqp_url: amqp 连接字符串
        :param exchange: exchange 名
        :param exchange_type: exchange 类型
        :param routing_key: 路由名字
        :param queue: queue 名，允许为空
        :param delivery_mode: 2: 消息持久化
        """
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.routing_key = routing_key

        # 默认消息持久化
        self.delivery_mode = delivery_mode

        self.appid = str(appid)

        self.queue = queue

        self._connection = None
        self._channel = None
        self._deliveries = None
        self._acked = None
        self._nacked = None
        self._message_number = 0
        self._stopping = False
        self._deliveries = []
        self._url = amqp_url

        self.connect()

    def connect(self):
        logger.info('Connecting to %s' % self._url)
        self._connection = pika.BlockingConnection(
            pika.URLParameters(self._url))
        logger.info('Connected')

        self.open_channel()

    def open_channel(self):
        if not self._channel:
            logger.info('Creating a new channel')
            self._channel = self._connection.channel()

            self.setup_exchange()

    def setup_exchange(self):
        logger.info('Declaring exchange %s' % self.exchange)

        # 当 delivery_mode 为 2 时，消息持久化， 所以 exchange 也需要持久化
        durable = self.delivery_mode == 2

        self._channel.exchange_declare(
            exchange=self.exchange,
            exchange_type=self.exchange_type,
            durable=durable
        )
        logger.info('Exchange declared')

    def enable_delivery_confirmations(self):
        """Send the Confirm.Select RPC method to RabbitMQ to enable delivery
        confirmations on the channel. The only way to turn this off is to close
        the channel and create a new one.

        When the message is confirmed from RabbitMQ, the
        on_delivery_confirmation method will be invoked passing in a Basic.Ack
        or Basic.Nack method from RabbitMQ that will indicate which messages it
        is confirming or rejecting.

        """
        self._channel.confirm_delivery(self.on_delivery_confirmation)

    def on_delivery_confirmation(self, method_frame):
        """Invoked by pika when RabbitMQ responds to a Basic.Publish RPC
        command, passing in either a Basic.Ack or Basic.Nack frame with
        the delivery tag of the message that was published. The delivery tag
        is an integer counter indicating the message number that was sent
        on the channel via Basic.Publish. Here we're just doing house keeping
        to keep track of stats and remove message numbers that we expect
        a delivery confirmation of from the list used to keep track of messages
        that are pending confirmation.

        :param pika.frame.Method method_frame: Basic.Ack or Basic.Nack frame

        """
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        logger.info('Received %s for delivery tag: %i' % (
                    confirmation_type,
                    method_frame.method.delivery_tag))
        if confirmation_type == 'ack':
            self._acked += 1
        elif confirmation_type == 'nack':
            self._nacked += 1
        self._deliveries.remove(method_frame.method.delivery_tag)
        logger.info('Published %i messages, %i have yet to be confirmed, '
                    '%i were acked and %i were nacked' % (
                    self._message_number, len(self._deliveries),
                    self._acked, self._nacked))

    def publish_message(self, message):
        if self._channel is None or not self._channel.is_open:
            return

        properties = pika.BasicProperties(
            app_id=self.appid,
            content_type='application/json',
            delivery_mode=self.delivery_mode
        )

        message = json.dumps(message, ensure_ascii=False)
        self._channel.basic_publish(self.exchange,
                                    self.routing_key,
                                    message,
                                    properties)
        self._message_number += 1
        self._deliveries.append(self._message_number)
        logger.info('Published message # %i: %s' % (self._message_number, message))

    def stop(self):
        logger.info('Stopping')
        self._stopping = True
        self.close_channel()
        self.close_connection()

    def close_channel(self):
        if self._channel is not None:
            logger.info('Closing the channel')
            self._channel.close()

    def close_connection(self):
        if self._connection is not None:
            logger.info('Closing connection')
            self._connection.close()


class AwardsMQPublisher(MQPublisher):

    TYPE_CLICK_JD = 0
    TYPE_APPLY = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_awards_click_jd(self, company_id, position_id, employee_id,
                            be_recom_user_id,
                            recom_user_id):
        self._add_awards(
            company_id, position_id, employee_id, be_recom_user_id,
            recom_user_id,
            type=self.TYPE_CLICK_JD)

    def add_awards_apply(self, company_id, position_id, employee_id,
                         be_recom_user_id,
                         recom_user_id):
        self._add_awards(
            company_id, position_id, employee_id, be_recom_user_id,
            recom_user_id,
            type=self.TYPE_APPLY)

    def _add_awards(self, company_id, position_id, employee_id,
                    be_recom_user_id, recom_user_id, type):
        params = {
            'companyId':     company_id,
            'positionId':    position_id,
            'recomUserId':   recom_user_id,
            'berecomUserId': be_recom_user_id,
            'employeeId':    employee_id
            }

        if type == self.TYPE_CLICK_JD:
            params.update({'templateId': const.RECRUIT_STATUS_RECOMCLICK_ID})
        elif type == self.TYPE_APPLY:
            params.update({'templateId': const.RECRUIT_STATUS_APPLY_ID})

        else:
            assert False  # should not be here

        self.publish_message(params)

amqp_url = 'amqp://{}:{}@{}:{}/%2F?connection_attempts={}&heartbeat_interval={}'.format(
    settings['rabbitmq_username'],
    settings['rabbitmq_password'],
    settings['rabbitmq_host'],
    settings['rabbitmq_port'],
    settings['rabbitmq_connection_attempts'],
    settings['rabbitmq_heartbeat_interval']
    )

award_publisher = AwardsMQPublisher(
    amqp_url=amqp_url,
    exchange="employee_exchange",
    exchange_type="topic",
    routing_key="reward.add",
    appid=6
)

def main():
    award_publisher = AwardsMQPublisher(
        amqp_url='amqp://guest:guest@localhost:5672/%2F?connection_attempts=3&heartbeat_interval=3600',
        exchange="employee_exchange",
        exchange_type="topic",
        routing_key="reward.add",
        appid=6
    )
    award_publisher.publish_message({"hello": "world123"})

if __name__ == '__main__':
    main()
