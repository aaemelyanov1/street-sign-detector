"""Pydantic модели для запросов и ответов API."""
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class StatusEnum(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class DetectionResult(BaseModel):
    """Одна детекция с bounding box и уверенностью."""
    class_name: str = Field(..., description="Название класса")
    bbox: List[float] = Field(..., description="Координаты bounding box: [x_min, y_min, width, height] в пикселях")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Уверенность модели")


class TaskResponse(BaseModel):
    """Ответ при создании задачи."""
    task_id: str = Field(..., description="UUID задачи")
    status_url: Optional[str] = Field(None, description="URL для проверки статуса")


class ResultResponse(BaseModel):
    """Ответ при запросе результата."""
    task_id: str
    status: StatusEnum
    detections: Optional[List[DetectionResult]] = None
    error_message: Optional[str] = None