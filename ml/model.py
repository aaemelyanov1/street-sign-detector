"""
Загрузка YOLO-модели из файла весов.
"""
import logging
import torch
from ultralytics import YOLO
from app.core.config import settings
from app.core.exceptions import ModelLoadError
import os

logger = logging.getLogger(__name__)

_model = None


def load_model() -> YOLO:
    """
    Возвращает загруженную модель YOLO. При первом вызове загружает из файла,
    при ошибке выбрасывает ModelLoadError.
    """
    global _model
    if _model is None:
        try:
            logger.info("Loading YOLO model from %s", settings.MODEL_WEIGHTS_PATH)
            _model = YOLO(settings.MODEL_WEIGHTS_PATH)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            _model.to(device)
            logger.info("Model loaded successfully on device: %s", device)
            if device == "cuda":
                logger.info("GPU: %s", torch.cuda.get_device_name(0))
        except Exception as e:
            logger.error("Failed to load model: %s", str(e))
            raise ModelLoadError(f"Cannot load model weights: {str(e)}") from e
    return _model