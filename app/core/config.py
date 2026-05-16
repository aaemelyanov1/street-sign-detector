"""Конфигурация приложения с помощью Pydantic Settings."""
from pydantic_settings import BaseSettings
from pathlib import Path
import os


class Settings(BaseSettings):
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_REQUESTS: str = "detection-requests"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Загрузка файлов
    UPLOAD_DIR: str = "/data/uploads"

    # Пороги
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.5

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"  # разрешить игнорировать неописанные переменные
    }

    MODEL_VERSION: str = "model_weights.pt"

    @property
    def MODEL_WEIGHTS_PATH(self) -> Path:
        return Path("ml/models") / self.MODEL_VERSION


settings = Settings()