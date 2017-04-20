# coding=utf-8

import redis
import unittest


class Subscriber(object):

    def __init__(self,
                 redis_client,
                 ignore_subscribe_messages=True,
                 sleep_time=0.01,
                 channel=None,
                 message_handler=None,
                 subscribe_mode='subscribe'):

        self._pubsub = redis_client.pubsub()
        self._pubsub.ignore_subscribe_messages = ignore_subscribe_messages

        if channel:
            if subscribe_mode == 'subscribe':
                self.subscribe(channel, message_handler)
            elif subscribe_mode == 'psubscribe':
                self.psubscribe(channel, message_handler)
            else:
                raise ValueError('invalid subscribe_mode')

        self._sleep_time = sleep_time
        self._thread = None

    def subscribe(self, channel, message_handler=None):
        if message_handler:
            self._pubsub.subscribe(**{channel: message_handler})
        else:
            self._pubsub.subscribe(channel)

    def psubscribe(self, channel, message_handler=None):
        if message_handler:
            self._pubsub.psubscribe(**{channel: message_handler})
        else:
            self._pubsub.psubscribe(channel)

    def start_run_in_thread(self):
        self._thread = self._pubsub.run_in_thread(sleep_time=self._sleep_time)

    def stop_run_in_thread(self):
        if self._thread is not None:
            self._thread.stop()

    def cleanup(self):
        self._pubsub.reset()
        self._thread = None
        self._sleep_time = 0.01


class TestSubscriber(unittest.TestCase):
    def test1(self):
        redis_client = redis.StrictRedis()

        def handler(message):
            data = message['data']
            print("handle message.data: %s" % data)

        subs = Subscriber(redis_client, channel='yiliang', message_handler=handler)
        subs.start_run_in_thread()
        redis_client.publish('yiliang', 'hey')
        redis_client.publish('yiliang', 'hey2')
        redis_client.publish('yiliang', 'hey3')
        subs.stop_run_in_thread()

if __name__ == '__main__':
    unittest.main()

