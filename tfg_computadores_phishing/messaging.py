from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Callable

import pika


@dataclass(frozen=True)
class RabbitMQSettings:
    url: str
    queue_name: str
    prefetch_count: int


def load_rabbitmq_settings() -> RabbitMQSettings:
    return RabbitMQSettings(
        url=os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F"),
        queue_name=os.getenv("RABBITMQ_QUEUE", "telegram_phishing_events"),
        prefetch_count=int(os.getenv("RABBITMQ_PREFETCH_COUNT", "10")),
    )


def _connect(settings: RabbitMQSettings) -> pika.BlockingConnection:
    params = pika.URLParameters(settings.url)
    params.heartbeat = 60
    params.blocked_connection_timeout = 120
    return pika.BlockingConnection(params)


def _declare_queue(channel, settings: RabbitMQSettings):
    return channel.queue_declare(queue=settings.queue_name, durable=True)


def get_queue_depth(settings: RabbitMQSettings) -> int | None:
    try:
        connection = _connect(settings)
        channel = connection.channel()
        result = channel.queue_declare(queue=settings.queue_name, durable=True, passive=True)
        depth = int(result.method.message_count)
        connection.close()
        return depth
    except Exception:
        return None


def publish_json_message(payload: dict[str, object], settings: RabbitMQSettings) -> int | None:
    connection = _connect(settings)
    channel = connection.channel()
    result = _declare_queue(channel, settings)
    channel.basic_publish(
        exchange="",
        routing_key=settings.queue_name,
        body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    depth = int(result.method.message_count) + 1
    connection.close()
    return depth


def consume_json_messages(
    settings: RabbitMQSettings,
    handler: Callable[[dict[str, object]], None],
) -> None:
    connection = _connect(settings)
    channel = connection.channel()
    _declare_queue(channel, settings)
    channel.basic_qos(prefetch_count=settings.prefetch_count)

    def _callback(channel, method, _properties, body: bytes) -> None:
        try:
            payload = json.loads(body.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("El mensaje de RabbitMQ no contiene un objeto JSON valido.")
            handler(payload)
        except Exception as exc:
            print(f"Worker error -> {exc}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        else:
            channel.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=settings.queue_name, on_message_callback=_callback)
    channel.start_consuming()
