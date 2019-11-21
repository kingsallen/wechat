# coding=utf-8

import pika
from pika import TornadoConnection
import pika_pool

import json
from globals import logger, env

import conf.common as const
from setting import settings


class Publisher(object):
    """
    rabbitMQ客户端实现
    部分方法（例如add_on_cancel_callback）只是记录了log，并没有做具体的实现，你通过重写这些方法，以实现各种功能
    当前pika版本为0.10.0，参考`https://github.com/pika/pika/blob/0.10.0/docs/examples/tornado_consumer.rst`
    """

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
        logger.debug('PikaClient Publisher: connected to RabbitMQ')
        self.connection = connection
        self.connection.add_on_close_callback(self.on_closed)
        self.connection.channel(self.on_channel_open)

    def on_closed(self, connection, reply_code, reply_text):
        logger.warning('PikaClient Publisher: rabbit connection closed, reopening in 1 seconds: (%s) %s', reply_code, reply_text)
        self.connection.add_timeout(1, self.reconnect)

    def reconnect(self):
        self.connection = self.connect()

    def on_channel_open(self, channel):
        """override this method to bind exchange"""
        # declare exchanges, which in turn, declare
        # queues, and bind exchange to queues
        logger.debug('PikaClient Publisher: Channel open, Declaring exchange {}'.format(self.exchange))
        self.channel = channel

    def publish_message(self, message, routing_key=""):
        properties = pika.BasicProperties(app_id=const.APPID[env],
                                          content_type='application/json',
                                          delivery_mode=2 if self.durable else 1)

        self.channel.basic_publish(
            self.exchange,
            routing_key or self.routing_key,
            json.dumps(message, ensure_ascii=False),
            properties
        )

    def on_channel_closed(self, channel, reply_code, reply_text):
        logger.warning('Publisher Channel closed, reopening in 1 seconds: (%s) %s',
                       reply_code, reply_text)
        self.channel.close()


award_publisher = Publisher(
    exchange="user_action_topic_exchange",
    exchange_type="topic",
)

data_userprofile_publisher = Publisher(
    exchange="data.user_profile",
    exchange_type="direct",
)

# 用户关注公众号后恢复用户员工身份
user_follow_wechat_publisher = Publisher(
    exchange="user_follow_wechat_exchange",
    exchange_type="direct",
)

# 用户取消关注公众号后取消员工身份
user_unfollow_wechat_publisher = Publisher(
    exchange="user_unfollow_wechat_exchange",
    exchange_type="direct",
)

# 所有未读赞的数量置空
unread_praise_publisher = Publisher(
    exchange="employee_view_leader_board_exchange",
    exchange_type="direct",
)

# 转发职位被点击
jd_click_publisher = Publisher(
    exchange="retransmit_click_exchange",
    exchange_type="topic",
)

# 转发职位被申请
jd_apply_publisher = Publisher(
    exchange="retransmit_apply_exchange",
    exchange_type="topic",
)


neo4j_position_forward = Publisher(
    exchange="employee_neo4j_exchange",
    exchange_type="direct",
)


# 为了兼容过去的代码，这里不优雅的实现了所有的connect
consumer_list = [
    award_publisher,
    data_userprofile_publisher,
    user_follow_wechat_publisher,
    user_unfollow_wechat_publisher,
    unread_praise_publisher,
    jd_click_publisher,
    jd_apply_publisher,
    neo4j_position_forward
]


def connect_all_client():
    for c in consumer_list:
        c.connect()


def main():
    award_publisher_test = Publisher(
        exchange="employee_exchange",
        exchange_type="topic",
        routing_key="reward.add",
    )

    award_publisher_test.publish_message({"hello": "world123"})


if __name__ == '__main__':
    main()
