"""Кастомные исключения."""

class TaskNotFoundException(Exception):
    # Ошибка задача не найденв.
    pass

class ModelPredictionError(Exception):
    # Ошибка предсказания ML-модели.
    pass

class ModelLoadError(Exception):
    # Ошибка загрузки ML-модели.
    pass