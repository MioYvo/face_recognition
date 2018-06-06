# coding=utf-8
# __author__ = 'Mio'
import json

import pika
from tornado.log import app_log

# from fetcher.jobs.sync_data import CommonSync
from fetcher.jobs.cloud_response import CloudResponse
from fetcher.utils.singleton import singleton
from fetcher.settings import (
    RABBIT_HOST, RABBIT_PORT, RABBIT_USER, RABBIT_PASSWORD, RABBIT_URL,
    RABBIT_EXCHANGE, RABBIT_EXCHANGE_TYPE,
    RABBIT_SELF_QUEUE_FORMAT,
    RABBIT_SELF_QUEUE_ROUTING_KEY,
    RECONNECT_INTERVAL_SECONDS)


# noinspection PyUnusedLocal
class Consumer(object):
    """This is an example consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.

    """

    def __init__(self, amqp_url, exchange, exchange_type, queue, routing_key):
        """Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        :param str amqp_url: The AMQP url to connect with

        """
        self.connecting = False
        self._connection = None
        self._channel = None
        self._consumer_tag = None
        self._url = amqp_url

        self.exchange = exchange
        self.exchange_type = exchange_type
        self.queue = queue
        self.routing_key = routing_key

    def on_connection_open(self, unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :type unused_connection: pika.SelectConnection

        """
        # app_log.info('Connection opened')
        app_log.info('连接已打开')
        self._connection = unused_connection
        self.add_on_connection_close_callback()
        self.open_channel()

    def on_connection_open_error_callback(self, connection, exception):
        """
         Called if the connection can't be established
        :param connection:
        :param exception: str
        :return:
        """
        app_log.info("连接失败 {} : {}".format(self._url, exception))
        self.connecting = False
        # check_connection will reconnect

    def add_on_connection_close_callback(self):
        """This method adds an on close callback that will be invoked by pika
        when RabbitMQ closes the connection to the publisher unexpectedly.

        """
        # app_log.info('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given

        """
        self._channel = None
        app_log.warning('Connection closed, reopening in {} second(s): ({}) {}'.format(
            RECONNECT_INTERVAL_SECONDS, reply_code, reply_text))
        self._connection.add_timeout(RECONNECT_INTERVAL_SECONDS, self.reconnect)

    def open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.

        """
        # app_log.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        # app_log.info('Channel opened')
        self.connecting = False
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.exchange)

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """
        # app_log.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed

        """
        app_log.warning('Channel %i was closed: (%s) %s',
                        channel, reply_code, reply_text)
        self.close_connection()

    def setup_exchange(self, exchange_name):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.

        :param str|unicode exchange_name: The name of the exchange to declare

        """
        # app_log.info('Declaring exchange %s', exchange_name)
        app_log.info('正在声明 exchange %s', exchange_name)
        self._channel.exchange_declare(callback=self.on_exchange_declareok,
                                       exchange=exchange_name,
                                       exchange_type=self.exchange_type,
                                       durable=True)

    def on_exchange_declareok(self, unused_frame):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame

        """
        # app_log.info('Exchange declared')
        app_log.info('Exchange 已声明')
        self.setup_queue(self.queue)

    def setup_queue(self, queue_name):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.

        :param str|unicode queue_name: The name of the queue to declare.

        """
        # app_log.info('Declaring queue %s', queue_name)
        app_log.info('正在声明 queue %s', queue_name)
        self._channel.queue_declare(self.on_queue_declareok, queue_name, durable=True)

    def on_queue_declareok(self, method_frame):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame

        """
        # app_log.info('Binding %s to %s with %s',
        self.bind_queue(queue=self.queue, exchange=self.exchange, routing_key=self.routing_key)

    def bind_queue(self, queue, exchange, routing_key):
        app_log.info('绑定 %s to %s with %s',
                     self.exchange, self.queue, self.routing_key)
        self._channel.queue_bind(callback=self.on_bindok, queue=queue, exchange=exchange, routing_key=routing_key)

    def on_bindok(self, unused_frame):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.

        :param pika.frame.Method unused_frame: The Queue.BindOk response frame

        """
        # app_log.info('Queue bound')
        app_log.info('Queue 已绑定')
        self.start_consuming()

    def start_consuming(self):
        """This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.

        """
        # app_log.info('Issuing consumer related RPC commands')
        app_log.info('消费者等待数据')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self.queue)

    def on_message(self, unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel unused_channel: The channel object
        :param pika.Spec.Basic.Deliver basic_deliver: basic_deliver method
        :param pika.Spec.BasicProperties properties: properties
        :param str|unicode body: The message body

        """
        # app_log.info('Received message # %s from %s: %s', basic_deliver.delivery_tag, properties.app_id, body[:10])
        app_log.info('收到消息 # %s from %s: %s', basic_deliver.delivery_tag, properties.app_id, body[:20])

        # lock = redis_lock.Lock(redis_client=r, name=DATA_SOURCE_NAME, id=datetime_2_string(local_now_dt()).encode(),
        #                        expire=EXPIRE_SECONDS_OF_REDIS_LOCK, auto_renewal=True)
        # if lock.acquire(timeout=TIMEOUT_SECONDS_OF_REDIS_LOCK):
        #     app_log.info("got lock")
        try:
            # SendData(body)
            _data = json.loads(body)
            """ from configurer.handlers.data_source.schema_data_response
            
                "data_source_id": Use(native_str),
                "status": And(Use(native_str), lambda x: x in (
                    DATA_RESPONSE_STATUS_START, DATA_RESPONSE_STATUS_ACCEPTED, DATA_RESPONSE_STATUS_REJECTED,
                    DATA_RESPONSE_STATUS_RESTART)),
                "total_slice": And(Use(int), lambda x: x >= 0),
                "current_slice": And(Use(int), lambda x: x >= 0),
                "syncing_date": Use(string_2_date),
                Optional("fetch_bunch_size"): And(Use(int), lambda x: x > 0),
                "msg": Use(native_str),
                Optional(object): object
            """
            # Job functions
            # CommonSync(**_data)
            CloudResponse(_data)
        except Exception as e:
            app_log.exception(e)

            # release the lock
        #     try:
        #         app_log.error('releasing lock')
        #         lock.release()
        #     except Exception as e:
        #         app_log.error(e)
        #
        #     app_log.info("lock released")
        # else:
        #     app_log.error("another job is already running at {}".format(lock.get_owner_id()))

        self.acknowledge_message(basic_deliver.delivery_tag)

    def acknowledge_message(self, delivery_tag):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.

        :param int delivery_tag: The delivery tag from the Basic.Deliver frame

        """
        # app_log.info('Acknowledging message %s', delivery_tag)
        app_log.info('确认消息(ack) %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.

        """
        # app_log.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame

        """
        app_log.info('Consumer was cancelled remotely, shutting down: %r', method_frame)
        if self._channel:
            self.close_channel()

    def on_cancelok(self, unused_frame):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method unused_frame: The Basic.CancelOk frame

        """
        app_log.info('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.

        """
        if self._channel:
            app_log.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """

        app_log.info('正在连接MQ: %s', self._url)
        if self.connecting is False:
            self.connecting = True
            self._connection = pika.adapters.TornadoConnection(
                parameters=pika.URLParameters(self._url),
                on_open_callback=self.on_connection_open,
                on_open_error_callback=self.on_connection_open_error_callback
            )
        else:
            app_log.info('another connection is making, MQ: %s', self._url)
            return

    def reconnect(self):
        """Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.

        """
        app_log.info("reconnecting ...")
        if self.connecting:
            app_log.warning("another consumer is connecting")
            return
        self.stop()

        # Create a new connection
        self._connection = None
        self._channel = None
        self._consumer_tag = None
        self._connection = self.connect()

    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.

        """
        app_log.info('Closing the channel')
        try:
            self._channel.close()
        except Exception as e:
            app_log.error(e)

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        app_log.info('Closing connection')
        try:
            self._connection.close()
        except Exception as e:
            app_log.error(e)

    def check_connection(self):
        if not self._channel or not self._connection:
            self.reconnect()

    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.

        """
        if self.connecting is True:
            app_log.info("another one is calling run()")
            return
        app_log.info("starting the consumer")
        self.connect()
        return self

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """
        app_log.info('Stopping')
        # self._closing = True
        self.stop_consuming()
        self.close_channel()
        self.close_connection()
        app_log.info('Stopped')


@singleton
class ConsumerSingleton(object):
    def __init__(self):
        self.consumer = Consumer(RABBIT_URL.format(
            user=RABBIT_USER, password=RABBIT_PASSWORD, host=RABBIT_HOST, port=RABBIT_PORT),
            exchange=RABBIT_EXCHANGE, exchange_type=RABBIT_EXCHANGE_TYPE,
            queue=RABBIT_SELF_QUEUE_FORMAT.format(func="data-response"),
            routing_key=RABBIT_SELF_QUEUE_ROUTING_KEY.format(func="data-response")
        )

    def start(self):
        self.consumer.run()

    def stop(self):
        self.consumer.stop()


# def consumer():
#     # _consumer = Consumer('amqp://h3c:1q2w3e@rabbitmq:5671/%2F')
#     _consumer = Consumer('amqp://localhost:5672/%2F')
#     try:
#         _consumer.run()
#     except KeyboardInterrupt:
#         _consumer.stop()


if __name__ == '__main__':
    ConsumerSingleton()
