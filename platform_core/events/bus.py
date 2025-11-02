"""
Async event bus using RabbitMQ for inter-plugin communication.
"""
import asyncio
import json
import logging
from typing import Any, Callable, Dict, Optional

import aio_pika
from aio_pika import ExchangeType, Message, connect_robust

from platform_core.config import settings

logger = logging.getLogger(__name__)


class EventBus:
    """RabbitMQ-based event bus for asynchronous communication."""

    def __init__(self, rabbitmq_url: str) -> None:
        self.url = rabbitmq_url
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
        self.subscribers: Dict[str, Callable[..., Any]] = {}

    async def connect(self) -> None:
        """Establish RabbitMQ connection."""
        self.connection = await connect_robust(self.url)
        self.channel = await self.connection.channel()

        # Create topic exchange for event routing
        self.exchange = await self.channel.declare_exchange(
            "network_platform_events", ExchangeType.TOPIC, durable=True
        )
        logger.info("Event bus connected to RabbitMQ")

    async def publish(
        self, event_type: str, payload: Dict[str, Any], tenant_id: str
    ) -> None:
        """Publish event to the bus."""
        if not self.exchange:
            raise RuntimeError("Event bus not connected")

        routing_key = f"{tenant_id}.{event_type}"
        message_body = json.dumps(
            {"event_type": event_type, "payload": payload, "tenant_id": tenant_id}
        )

        await self.exchange.publish(
            Message(body=message_body.encode()), routing_key=routing_key
        )
        logger.debug(f"Published event: {routing_key}")

    async def subscribe(
        self,
        event_pattern: str,
        handler: Callable[..., Any],
        queue_name: Optional[str] = None,
    ) -> None:
        """Subscribe to events matching pattern (e.g., '*.device.added')."""
        if not self.channel:
            raise RuntimeError("Event bus not connected")

        queue = await self.channel.declare_queue(
            queue_name or f"queue_{event_pattern}", durable=True
        )
        await queue.bind(self.exchange, routing_key=event_pattern)

        async def process_message(message: aio_pika.IncomingMessage) -> None:
            async with message.process():
                try:
                    event_data = json.loads(message.body.decode())
                    await handler(event_data)
                except Exception as e:
                    logger.error(f"Error processing event: {e}")

        await queue.consume(process_message)
        logger.info(f"Subscribed to events: {event_pattern}")


# Global event bus instance
event_bus = EventBus(settings.RABBITMQ_URL)
