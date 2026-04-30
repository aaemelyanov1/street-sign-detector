"""Зависимости FastAPI для получения продюсера Kafka и клиента Redis."""
from fastapi import Request
from app.services.kafka_producer import KafkaProducerManager
from app.services.result_storage import ResultStorage


def get_kafka_producer(request: Request) -> KafkaProducerManager:
    return request.app.state.kafka_producer


def get_redis_client(request: Request) -> ResultStorage:
    return request.app.state.redis_client