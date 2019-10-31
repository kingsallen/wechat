# coding:UTF-8

"""
Kafka client for MoSeeker's Python project
a wrapper around Confluent's official Python client lib
https://github.com/confluentinc/confluent-kafka-python
"""

import datetime
import json
from abc import ABC, abstractmethod

from confluent_kafka import Producer

from setting import settings


# 6个事件 - 触发计算员工人脉雷达
# 1 新增浏览行为导致数据库链路改变 - java service
# 2 *pv实时统计 - python wechat*
# 3 候选人点击“联系内推”求推荐 - java service
# 4 候选人投递 - java service
# 5 候选人被推荐 - java service
# 6 候选人被邀请投递 - java service

# TODO:
# 1.add tests

class KafkaProducer:
    def __init__(self, config):
        self._config = config
        self.start()
        # TODO: add start stop

    def start(self):
        self._producer = Producer(self._config)  # TODO: does it actually connect to kafka?

    def stop(self):
        pass

    def send(self, topic, raw_content, force=False):
        """
        往某个topic发送内容
        :param topic: str
        :param content: bytes
        :return:
        """
        self._producer.produce(topic, raw_content)
        if force:
            self._producer.flush()


class RadarEventEmitter:
    def __init__(self, producer):
        self._producer = producer
        self._events = set()

    def register_event(self, event_type):
        """
        注册可以发送的事件
        :param event_type: Event, 时间类型
        :return: None
        """
        self._events.add(event_type)
        return self

    def emit(self, event):
        """
        发送事件
        :param event:
        :return:
        """
        if type(event) not in self._events:
            return
        self._producer.send(event.topic, event.serialized_content, force=True)


class Event(ABC):
    @property
    def serialized_content(self):
        return json.dumps(self.get_content()).encode("UTF-8")

    @abstractmethod
    def get_content(self):
        pass


class PositionPageViewEvent(Event):
    topic = "radar_position_page_view"
    event_name = "position_page_view"

    def __init__(self, user_id, company_id, position_id, employee_user_id, recom_user_id, click_from, source, send_time,
                 psc):
        self.user_id = user_id
        self.company_id = company_id
        self.position_id = position_id
        self.employee_user_id = employee_user_id
        self.event_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        self.recom_user_id = recom_user_id
        self.click_from = click_from
        self.source = source
        self.send_time = send_time
        self.psc = psc

    def get_content(self):
        c = {"event_time": self.event_time, "event": self.event_name}
        c.update(self.__dict__)
        return c


config = {'bootstrap.servers': settings['kafka_servers']}
kafka_producer = KafkaProducer(config)


def main():
    config = {'bootstrap.servers': 'localhost:9092'}
    kafka_producer = KafkaProducer(config)
    # kafka_producer.start()

    radar_event_emitter = RadarEventEmitter(kafka_producer)
    radar_event_emitter.register_event(PositionPageViewEvent)

    for i in range(100):
        position_page_view_event = PositionPageViewEvent(
            user_id=131, company_id=1234, position_id=38917, employee_user_id=456, recom_user_id=0, click_from=1, source=0, send_time=1)
        radar_event_emitter.emit(position_page_view_event)


if __name__ == "__main__":
    main()
