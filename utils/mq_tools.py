__author__ = 'zhaobin022'
import pika

def get_mq_conn():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
                   'localhost'))
    return connection