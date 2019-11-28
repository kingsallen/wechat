# coding=utf-8

import pika
import pika_pool
import time

import time

import json
from globals import logger

import conf.common as const
from setting import settings


class MQPublisher(object):

    def __init__(self, amqp_url, exchange, exchange_type, appid,
                 default_routing_key="", queue="", delivery_mode=2):
        """ Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        :param amqp_url: amqp 连接字符串
        :param exchange: exchange 名
        :param exchange_type: exchange 类型
        :param default_routing_key: 默认路由键
        :param queue: queue 名，允许为空
        :param delivery_mode: 2: 消息持久化
        """
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.default_routing_key = default_routing_key

        # 默认消息持久化
        self.delivery_mode = delivery_mode

        self.appid = str(appid)
        self.queue = queue

        self._pool = None
        self._deliveries = None
        self._message_number = 0
        self._url = amqp_url

        self.connect()

    def connect(self):
        logger.info('Connecting to %s' % self._url)
        self._pool = pika_pool.QueuedPool(
            create=lambda: pika.BlockingConnection(
                parameters=pika.URLParameters(self._url)),
            max_size=50,
            max_overflow=50,
            timeout=10,
            recycle=3600,
            stale=10)
        logger.info('Connected')

    def publish_message(self, message, routing_key=None):

        # TODO (tangyiliang) Add random message id
        start = time.time()
        with self._pool.acquire() as cxt:
            properties = pika.BasicProperties(
                app_id=self.appid,
                content_type='application/json',
                delivery_mode=self.delivery_mode
            )

            message = json.dumps(message, ensure_ascii=False)

            if not routing_key:
                routing_key = self.default_routing_key

            cxt.channel.basic_publish(
                body=message,
                exchange=self.exchange,
                routing_key=routing_key,
                properties=properties
            )

            self._message_number += 1
            end = time.time()
            logger.info(
                'Published message # %i: body:%s, exchange:%s, routing_key:%s, time:%s' % (
                    self._message_number, message, self.exchange, routing_key, (end-start)*1000))


class AwardsMQPublisher(MQPublisher):

    TYPE_CLICK_JD = 0
    TYPE_APPLY = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_awards_click_jd(self, company_id, position_id, employee_id, be_recom_user_id, recom_user_id):
        self._add_awards(company_id, position_id, employee_id, be_recom_user_id, recom_user_id, type=self.TYPE_CLICK_JD)

    def add_awards_apply(self, company_id, position_id, employee_id, be_recom_user_id, recom_user_id, application_id):
        self._add_awards(company_id, position_id, employee_id, be_recom_user_id, recom_user_id, type=self.TYPE_APPLY, application_id=application_id)

    def _add_awards(self, company_id, position_id, employee_id, be_recom_user_id, recom_user_id, type, **kwargs):
        params = {
            'companyId':     company_id,
            'positionId':    position_id,
            'recomUserId':   recom_user_id,
            'berecomUserId': be_recom_user_id,
            'employeeId':    employee_id
            }

        if type == self.TYPE_CLICK_JD:
            params.update({'templateId': const.RECRUIT_STATUS_RECOMCLICK_ID})
            routing_key = "sharejd.jd_clicked"
        elif type == self.TYPE_APPLY:
            params.update({'templateId': const.RECRUIT_STATUS_APPLY_ID,
                           'applicationId': kwargs['application_id']})
            routing_key = "sharejd.job_applied"

        else:
            assert False  # should not be here

        self.publish_message(message=params, routing_key=routing_key)


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
    exchange="user_action_topic_exchange",
    exchange_type="topic",
    appid=6
)

data_userprofile_publisher = MQPublisher(
    amqp_url=amqp_url,
    exchange="data.user_profile",
    exchange_type="direct",
    appid=6
)

# 用户关注公众号后恢复用户员工身份
user_follow_wechat_publisher = MQPublisher(
    amqp_url=amqp_url,
    exchange="user_follow_wechat_exchange",
    exchange_type="direct",
    appid=6
)

# 用户取消关注公众号后取消员工身份
user_unfollow_wechat_publisher = MQPublisher(
    amqp_url=amqp_url,
    exchange="user_unfollow_wechat_exchange",
    exchange_type="direct",
    appid=6
)

# 所有未读赞的数量置空
unread_praise_publisher = MQPublisher(
    amqp_url=amqp_url,
    exchange="employee_view_leader_board_exchange",
    exchange_type="direct",
    appid=6
)

# 转发职位被点击
jd_click_publisher = MQPublisher(
    amqp_url=amqp_url,
    exchange="retransmit_click_exchange",
    exchange_type="topic",
    appid=6
)

# 转发职位被申请
jd_apply_publisher = MQPublisher(
    amqp_url=amqp_url,
    exchange="retransmit_apply_exchange",
    exchange_type="topic",
    appid=6
)


neo4j_position_forward = MQPublisher(
    amqp_url=amqp_url,
    exchange="employee_neo4j_exchange",
    exchange_type="direct",
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
