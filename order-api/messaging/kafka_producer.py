import json
import os

from aiokafka import AIOKafkaProducer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = "orders"

_producer: AIOKafkaProducer | None = None


async def start():
    global _producer
    _producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await _producer.start()


async def stop():
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None


async def publish_order_event(order_id: str, data: dict):
    if not _producer:
        return
    event = json.dumps({"event": "ORDER_CREATED", "order_id": order_id, **data}).encode()
    await _producer.send_and_wait(TOPIC, event)
