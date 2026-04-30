"""
Загрузка YOLO-модели из файла весов.
"""
import logging
from ultralytics import YOLO
from app.core.config import settings
from app.core.exceptions import ModelLoadError

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
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error("Failed to load model: %s", str(e))
            raise ModelLoadError(f"Cannot load model weights: {str(e)}") from e
    return _model