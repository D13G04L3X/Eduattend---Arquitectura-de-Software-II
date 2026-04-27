# src/notification_service/infrastructure/adapters/inbound/__init__.py
from .rabbitmq_consumer import RabbitMQConsumer

__all__ = ["RabbitMQConsumer"]
