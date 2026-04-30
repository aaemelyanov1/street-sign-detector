"""
Инференс YOLO на одном изображении.
"""
import logging
from pathlib import Path
from typing import List, Dict
from PIL import Image
from app.core.config import settings
from ml.model import load_model

logger = logging.getLogger(__name__)

CLASS_NAMES_MAP = {
    "3_24": "Ограничение скорости 50",
    "2_1": "Главная дорога",
    # ... остальные 153 класса
}

def predict_from_file(image_path: str, confidence_threshold: float) -> List[Dict]:
    """
    Детектирует дорожные знаки на изображении.
    Args:
        image_path: путь к файлу (в shared volume)
        confidence_threshold: минимальная уверенность
    Returns:
        список словарей с ключами: class_name, bbox, confidence
    """
    model = load_model()
    try:
        # Верификация, что файл можно открыть
        with Image.open(image_path) as img:
            img.verify()
    except Exception as e:
        raise ModelPredictionError(f"Cannot open image file: {e}")

    # Инференс YOLO
    results = model.predict(
        source=image_path,
        conf=confidence_threshold,
        verbose=False
    )

    detections = []
    if len(results) == 0:
        return detections

    # results[0] — первый (единственный) источник
    result = results[0]
    if result.boxes is None:
        return detections

    for box in result.boxes:
        # xyxy в пикселях
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        class_id = int(box.cls[0])
        class_name = model.names[class_id]

        width = x2 - x1
        height = y2 - y1
        detections.append({
            "class_name": class_name,
            "bbox": [round(x1, 2), round(y1, 2), round(width, 2), round(height, 2)],
            "confidence": round(conf, 4)
        })

    logger.debug("Detected %d objects", len(detections))
    return detections
