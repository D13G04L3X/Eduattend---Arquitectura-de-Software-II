# src/notification_service/infrastructure/adapters/inbound/rabbitmq_consumer.py
import json
import logging
import time

import pika

from ....application.send_absence_alert_use_case import SendAbsenceAlertUseCase

LOGGER = logging.getLogger(__name__)


class RabbitMQConsumer:
    def __init__(
        self,
        rabbitmq_url: str,
        use_case: SendAbsenceAlertUseCase,
        retry_delay_seconds: int = 5,
        max_retries: int = 5,
    ) -> None:
        self._rabbitmq_url = rabbitmq_url
        self._use_case = use_case
        self._retry_delay_seconds = retry_delay_seconds
        self._max_retries = max_retries

    def start_consuming(self) -> None:
        connection = self._connect_with_retry()
        if connection is None:
            LOGGER.error("No se pudo conectar a RabbitMQ despues de los reintentos.")
            return

        channel = connection.channel()
        channel.exchange_declare(
            exchange="absence_events",
            exchange_type="direct",
            durable=True,
        )
        channel.queue_declare(queue="absence_events", durable=True)
        channel.queue_bind(
            queue="absence_events",
            exchange="absence_events",
            routing_key="absence_limit",
        )

        def on_message(ch, method, properties, body):
            try:
                event_payload = json.loads(body.decode("utf-8"))
                self._use_case.execute(event_payload)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as exc:
                LOGGER.error("Error procesando evento de ausencia: %s", exc)
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue="absence_events", on_message_callback=on_message)

        LOGGER.info("Notification service escuchando eventos de ausencia...")
        try:
            channel.start_consuming()
        finally:
            if connection.is_open:
                connection.close()

    def _connect_with_retry(self):
        for attempt in range(1, self._max_retries + 1):
            try:
                parameters = pika.URLParameters(self._rabbitmq_url)
                return pika.BlockingConnection(parameters)
            except Exception as exc:
                LOGGER.warning(
                    "Intento %s/%s de conexion a RabbitMQ fallido: %s",
                    attempt,
                    self._max_retries,
                    exc,
                )
                if attempt < self._max_retries:
                    time.sleep(self._retry_delay_seconds)
        return None
