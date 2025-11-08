"""
RabbitMQ Connection Manager and Event Publisher.
"""
import aio_pika
import logging
from platform_core.config import get_settings

logger = logging.getLogger(__name__)

class RabbitMQManager:
    """Manages the connection to RabbitMQ and provides an event publishing interface."""

    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.connection = None
        self.channel = None

    async def connect(self):
        """Establishes the connection and channel."""
        try:
            self.connection = await aio_pika.connect_robust(self.amqp_url)
            self.channel = await self.connection.channel()
            logger.info("✅ RabbitMQ connection established.")
        except aio_pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def close(self):
        """Closes the channel and connection."""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
        logger.info("RabbitMQ connection closed.")

    async def publish_event(self, routing_key: str, message_body: str):
        """
        Publishes an event to the default exchange.

        Args:
            routing_key: The routing key for the message (e.g., "site.created").
            message_body: The message payload as a string (e.g., a JSON string).
        """
        if not self.channel:
            logger.error("Cannot publish event: RabbitMQ channel is not available.")
            return

        message = aio_pika.Message(
            body=message_body.encode(),
            content_type="application/json",
        )

        # Using the default exchange
        await self.channel.default_exchange.publish(
            message,
            routing_key=routing_key,
        )
        logger.info(f"Published event with routing key '{routing_key}'")


_rabbitmq_manager = None

def get_rabbitmq_manager() -> RabbitMQManager:
    """
    Returns a singleton instance of the RabbitMQManager.
    """
    global _rabbitmq_manager
    if _rabbitmq_manager is None:
        settings = get_settings()
        _rabbitmq_manager = RabbitMQManager(settings.RABBITMQ_URL)
    return _rabbitmq_manager
