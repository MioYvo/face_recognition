# coding=utf-8
# __author__ = 'Mio'
import asyncio
import json
from tornado.log import app_log as logging
from collections import defaultdict

from functools import partial

from typing import Callable, Any, Generator

from aio_pika import connect_robust
from aio_pika.patterns.base import Base
from aio_pika.queue import Queue
from aio_pika.exchange import Exchange
# noinspection PyProtectedMember
from aio_pika.exchange import ExchangeType
# noinspection PyProtectedMember
from aio_pika.message import IncomingMessage, Message, DeliveryMode, ReturnedMessage
from pika.exceptions import ChannelClosed

# from fetcher.settings import loop as default_loop
from .singleton import singleton
from .json_encoder import MySQLQueryEncoder


class Consumer(object):
    # __slots__ = 'queue', 'consumer_tag', 'loop',

    def __init__(self, queue: Queue, exchange: Exchange, routing_key: str, consumer_tag: str, loop):
        self.queue = queue
        self.exchange = exchange
        self.routing_key = routing_key
        self.consumer_tag = consumer_tag
        self.loop = loop

    def close(self) -> asyncio.Task:
        """ Cancel subscription to the channel

        :return: :class:`asyncio.Task`
        """

        async def closer():
            await self.queue.cancel(self.consumer_tag)

        return self.loop.create_task(closer())


@singleton
class AsyncRabbit(Base):
    CONTENT_TYPE = 'application/json'
    DELIVERY_MODE = DeliveryMode.PERSISTENT

    __doc__ = """
    Implements Master/Worker pattern.
    Usage example:

    `worker.py` ::

        master = Master(channel)
        worker = await master.create_worker('test_worker', lambda x: print(x))

    `master.py` ::

        master = Master(channel)
        await master.proxy.test_worker('foo')
    """

    def __init__(self, loop: asyncio.AbstractEventLoop, uri: str, exchange_name: str,
                 exchange_type=ExchangeType.DIRECT):
        """
        Creates a new :class:`Master` instance.
        :param loop:
        :param uri:
        :param exchange_name:
        :param exchange_type:
        """
        self.uri = uri
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type

        self.loop = loop

        self.consumers = defaultdict(list)

        self.connection = None
        self.channel = None
        self.exchange = None

        self.loop.run_until_complete(self.connect())

    async def connect(self):
        logging.info("connecting")
        # RobustConnection.connect will call `on_reconnect` of its channel, exchange and queue
        # Auto Reconnect is not reliable, fxxk aio-pika
        self.connection = await connect_robust(self.uri, loop=self.loop)

        self.channel = await self.connection.channel()
        self.channel.add_on_return_callback(self.on_message_returned)
        self.channel.add_close_callback(self.on_channel_closed_gw)

        await self.channel.set_qos(prefetch_count=1)

        self.exchange = await self.channel.declare_exchange(
            name=self.exchange_name,
            type=self.exchange_type,
            durable=True
        )

    def on_message_returned(self, message: ReturnedMessage):
        logging.warning(
            "Message returned. Probably destination queue does not exists: %r",
            message
        )

    async def reconnect(self):
        logging.info("reconnecting")
        try:
            self.connection.close()
        except Exception as e:
            logging.error(e)
            await self.connect()
        else:
            await asyncio.sleep(2, loop=self.loop)
            await self.connect()

    # noinspection PyUnusedLocal
    def on_channel_closed_gw(self, *args, **kwargs):
        self.loop.create_task(self.reconnect())
        # self.loop.run_until_complete(self.connect())

    def serialize(self, data: Any) -> bytes:
        """
        Serialize data to the bytes.
        :param data: Data which will be serialized
        :returns: bytes
        """
        return bytes(json.dumps(data, ensure_ascii=False, cls=MySQLQueryEncoder), 'utf-8')

    def deserialize(self, data: bytes) -> Any:
        return json.loads(data.decode('utf-8'))
        # return json.loads(data.decode('utf-8'), ensure_ascii=False, cls=MySQLQueryEncoder)

    @classmethod
    async def execute(cls, func, kwargs):
        kwargs = kwargs or {}
        result = await func(**kwargs)
        return result

    async def on_message(self, func, message: IncomingMessage):
        with message.process(requeue=True, ignore_processed=True):
            data = self.deserialize(message.body)
            # logging.info(f"on_message: got data: {data}")
            try:
                await self.execute(func, data)
            except ChannelClosed as e:
                logging.error(e)
                await self.connect()
                await self.execute(func, data)

    def create_consumer(self, queue_name: str, routing_key: str,
                        func: Callable,
                        **queue_kwargs):
        return self.loop.run_until_complete(self.do_create_consumer(queue_name, routing_key, func, **queue_kwargs))

    async def do_create_consumer(self,
                                 queue_name: str, routing_key: str,
                                 func: Callable,
                                 **queue_kwargs) -> [Generator, Any, None, Consumer]:
        """ Creates a new :class:`Worker` instance. """

        if queue_kwargs.get('durable') is None:
            queue_kwargs['durable'] = True

        queue = await self.channel.declare_queue(queue_name, **queue_kwargs)
        # bind queue to exchange
        await queue.bind(exchange=self.exchange, routing_key=routing_key)
        logging.info("bind queue {} to exchange {} with routing_key {}".format(queue, self.exchange, routing_key))
        # consume messages from queue
        consumer_tag = await queue.consume(
            partial(
                self.on_message,
                asyncio.coroutine(func)
            )
        )

        self.consumers[queue_name].append(
            Consumer(
                queue=queue, exchange=self.exchange, routing_key=routing_key,
                consumer_tag=consumer_tag,
                loop=self.loop
            )
        )
        return self

    def create_task(self, data: dict, routing_key: str = None, queue: str = None):
        self.loop.create_task(self.do_create_task(data=data, routing_key=routing_key, queue=queue))

    async def do_create_task(self, data: dict, routing_key: str = None, queue: str = None):
        """ Creates a new task for the worker """
        logging.info("Creating TASK to {}".format(routing_key or queue))
        if not (routing_key or queue):
            raise Exception("args routing_key or queue required")

        message = Message(
            body=self.serialize(data or {}),
            content_type=self.CONTENT_TYPE,
            delivery_mode=self.DELIVERY_MODE,
        )

        try:
            await self.do_publish(routing_key=routing_key, message=message, queue=queue)
        except Exception as e:
            logging.error(e)
            await self.reconnect()
            await asyncio.sleep(2, loop=self.loop)
            # await self.connect()
            await self.do_publish(routing_key=routing_key, message=message, queue=queue)

    async def do_publish(self, routing_key, message, queue):
        logging.info("publishing")
        if routing_key:
            await self.exchange.publish(
                message, routing_key, mandatory=True
            )
        else:
            await self.channel.default_exchange.publish(
                message, queue, mandatory=True
            )

    def stop(self):
        self.loop.create_task(self.do_stop())

    async def do_stop(self):
        """
        stop the rabbit channel, cancel consume from queue
        :return:
        """
        for queue_name in self.consumers:
            for consumer in self.consumers[queue_name]:
                consumer.close()
        await self.channel.close()
        self.connection.close()


if __name__ == '__main__':
    # _loop = asyncio.new_event_loop()
    # r = AsyncRabbit(_loop, uri="amqp://guest:guest@192.168.215.240:5672/",
    #                 exchange_name="one")
    # from configurer.handlers.send_data_to_cloud import DataSourceSendData
    #
    # r.master.create_worker("parser-yvonne", DataSourceSendData, durable=True)
    #
    # _loop.create_task(r)
    pass
