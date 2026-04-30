"""
Асинхронный продюсер Kafka.
Отправляет сообщения с задачей в формате JSON.
"""
import json
import logging
from aiokafka import AIOKafkaProducer
from app.core.config import settings

logger = logging.getLogger(__name__)


class KafkaProducerManager:
    def __init__(self, bootstrap_servers: str, topic: str):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer: AIOKafkaProducer | None = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        await self.producer.start()
        logger.info("Kafka producer started")

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")

    async def send_request(self, task_id: str, image_path: str, confidence_threshold: float):
        message = {
            "task_id": task_id,
            "image_path": image_path,
            "confidence_threshold": confidence_threshold
        }
        await self.producer.send_and_wait(self.topic, message)
        logger.debug("Message sent", extra={"task_id": task_id})