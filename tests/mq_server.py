# coding=utf-8
import pika
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_exchange',
                         type='topic')

result = channel.queue_declare(queue='topic_queue')
queue_name = result.method.queue


channel.queue_bind(
    exchange='topic_exchange', queue=queue_name, routing_key="topic_routing_key")

print(' [*] Waiting for messages. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))

channel.basic_consume(
    callback, queue=queue_name, no_ack=True)

channel.start_consuming()
