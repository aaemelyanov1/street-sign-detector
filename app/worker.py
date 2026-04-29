import asyncio
import logging
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.services.kafka_consumer import KafkaConsumerManager
from app.services.result_storage import ResultStorage
from ml.predict import predict_from_file
from ml.model import load_model, ModelLoadError

setup_logging()
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting worker")

    # Попытка загрузить модель при запуске
    try:
        load_model()  # кеширует в глобальную переменную
    except ModelLoadError as e:
        logger.critical("Cannot start worker: %s", str(e))
        raise SystemExit(1)

    redis_client = ResultStorage(redis_url=settings.REDIS_URL)
    await redis_client.connect()

    async def handle_message(task_id: str, image_path: str, confidence_threshold: float):
        try:
            detections = predict_from_file(image_path, confidence_threshold)
            await redis_client.set_result(task_id, detections)
            logger.info("Task completed", extra={"task_id": task_id, "detections_count": len(detections)})
        except Exception as e:
            logger.error("Task failed", extra={"task_id": task_id, "error": str(e)})
            await redis_client.set_error(task_id, str(e))

    consumer_manager = KafkaConsumerManager(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        topic=settings.KAFKA_TOPIC_REQUESTS,
        group_id="detection-worker-group",
        message_handler=handle_message
    )

    await consumer_manager.start()
    try:
        await asyncio.Future()
    finally:
        await consumer_manager.stop()
        await redis_client.close()

if __name__ == "__main__":
    asyncio.run(main())
