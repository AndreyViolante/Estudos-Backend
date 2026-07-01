import json
import os

import aio_pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
QUEUE_NAME = "orders"

_connection: aio_pika.RobustConnection | None = None


async def connect():
    global _connection
    _connection = await aio_pika.connect_robust(RABBITMQ_URL)


async def close():
    global _connection
    if _connection and not _connection.is_closed:
        await _connection.close()
    _connection = None


async def publish_order_created(order_id: str, data: dict):
    if not _connection or _connection.is_closed:
        return
    async with _connection.channel() as channel:
        await channel.declare_queue(QUEUE_NAME, durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps({"order_id": order_id, **data}).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=QUEUE_NAME,
        )
