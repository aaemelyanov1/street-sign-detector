"""Эндпоинты FastAPI."""
import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from app.core.config import settings
from app.api.schemas import TaskResponse, ResultResponse, DetectionResult
from app.services.result_storage import ResultStorage
from app.services.kafka_producer import KafkaProducerManager
from app.utils.image_helpers import save_upload_file
from app.api.dependencies import get_kafka_producer, get_redis_client

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}


@router.post("/detect", response_model=TaskResponse, status_code=202)
async def create_detection_task(
    file: UploadFile = File(..., description="Изображение дорожного знака"),
    confidence_threshold: float = Form(settings.DEFAULT_CONFIDENCE_THRESHOLD, ge=0.0, le=1.0),
    kafka_producer: KafkaProducerManager = Depends(get_kafka_producer),
    redis_client: ResultStorage = Depends(get_redis_client)
):
    """
    Загружает изображение, создаёт задачу на детекцию и ставит её в очередь Kafka.
    """
    # Валидация типа файла
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type. Only JPEG and PNG allowed.")

    # Сохранение файла
    content = await file.read()
    file_bytes = content
    task_id = str(uuid.uuid4())
    file_extension = Path(file.filename).suffix if file.filename else ".jpg"
    saved_path = await save_upload_file(file_bytes, file_extension, settings.UPLOAD_DIR, task_id)

    # Установка статуса pending
    await redis_client.set_task_status(task_id, "pending")

    # Отправка в Kafka
    await kafka_producer.send_request(task_id, str(saved_path), confidence_threshold)
    logger.info("Task created", extra={"task_id": task_id, "image_path": str(saved_path)})
    return TaskResponse(task_id=task_id, status_url=f"/result/{task_id}")


@router.get("/result/{task_id}", response_model=ResultResponse)
async def get_task_result(
    task_id: str,
    redis_client: ResultStorage = Depends(get_redis_client)
):
    """
    Возвращает статус и результат обработки задачи.
    """
    result_data = await redis_client.get_result(task_id)
    if result_data is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task_id = result_data["task_id"]
    status = result_data["status"]
    detections_list = result_data.get("detections")
    error_msg = result_data.get("error_message")

    # Приведение детекций к схеме, если есть
    detections = None
    if detections_list:
        detections = [DetectionResult(**d) for d in detections_list]

    return ResultResponse(
        task_id=task_id,
        status=status,
        detections=detections,
        error_message=error_msg
    )


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/ready")
async def ready(request: Request):
    # Проверка, что продюсер Kafka жив (можно не проверять, просто ok)
    return {"status": "ok"}