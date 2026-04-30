"""Вспомогательные функции для ML (заглушка)."""
from typing import List, Dict


def nms(detections: List[Dict], iou_threshold: float = 0.5) -> List[Dict]:
    """
    Заглушка Non-Maximum Suppression.
    Просто возвращает входной список без изменений.
    """
    return detections