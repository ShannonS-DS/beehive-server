#!/usr/bin/env python3
import argparse
import functools
import pika
import sys
import time

''' 
    declare a queue with a callback that transfers data from the queue to an exchange
'''
   
#________________________________________________________________________
def CallbackPushToExchange(channel, method, properties, body, theExchange):
    print('  CallbackPushToExchange:  {}  body = {}'.format(theExchange, body))
    channel.basic_publish(exchange = theExchange,
                      routing_key = '',
                      body = body)
    channel.basic_ack(delivery_tag = method.delivery_tag)

    
#________________________________________________________________________
if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument('exchangeSrc')
    argParser.add_argument('queue')
    argParser.add_argument('exchangeDest')
    argParser.add_argument('-durable')
    args = argParser.parse_args()
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    print("{}:  exchangeSrc = '{}', queue = '{}', exchangeDest = '{}'".format(sys.argv[0], 
                                                                    args.exchangeSrc, 
                                                                    args.queue, 
                                                                    args.exchangeDest))
    
    channel.queue_declare(queue = args.queue)
    
    channel.queue_bind(exchange = args.exchangeSrc, queue = args.queue)

    channel.basic_consume(functools.partial(CallbackPushToExchange, theExchange = args.exchangeDest), 
                            queue = args.queue)
    channel.basic_qos(prefetch_count=1)
    channel.start_consuming()
