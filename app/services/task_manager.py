"""Вспомогательные функции для работы с задачами (пока только генерация ID)."""
import uuid


class TaskManager:
    @staticmethod
    def generate_task_id() -> str:
        return str(uuid.uuid4())