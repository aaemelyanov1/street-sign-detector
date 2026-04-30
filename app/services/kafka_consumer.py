"""
Асинхронный консьюмер Kafka для обработки задач детекции.
"""
import json
import logging
from typing import Callable, Awaitable
from aiokafka import AIOKafkaConsumer

logger = logging.getLogger(__name__)


class KafkaConsumerManager:
    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        group_id: str,
        message_handler: Callable[[str, str, float], Awaitable[None]]
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.message_handler = message_handler
        self.consumer: AIOKafkaConsumer | None = None

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=False
        )
        await self.consumer.start()
        logger.info("Kafka consumer started, listening to topic: %s", self.topic)

        try:
            async for msg in self.consumer:
                try:
                    task_data = msg.value
                    task_id = task_data["task_id"]
                    image_path = task_data["image_path"]
                    confidence_threshold = task_data.get("confidence_threshold", 0.5)

                    logger.info("Processing message", extra={"task_id": task_id})
                    await self.message_handler(task_id, image_path, confidence_threshold)

                    # Ручное подтверждение после успешной обработки
                    await self.consumer.commit()
                except Exception as e:
                    logger.error("Error processing message", extra={"error": str(e)})
                    # Можно добавить политику повторов или оставить commit,
                    # чтобы не застревать. Пока пропускаем.
                    await self.consumer.commit()
        finally:
            await self.stop()

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")