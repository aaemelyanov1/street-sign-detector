# Stret Sign Detection (RTSD)

Веб-приложение для обнаружения дорожных знаков на изображениях (YOLO + FastAPI).  
**Текущий статус:** MVP, инференс через API, контейнеризация для CPU.

## Быстрый старт

### 1. Клонирование
```bash
git lfs install          # если ещё не установлен Git LFS
git clone https://github.com/Timeyan/street-sign-detector
cd <папка_проекта>
git lfs pull             # загрузить файлы моделей, когда они появятся
```

### 2. Переменные окружения
Создайте .env из примера:
```bash
cp .env.example .env
```
В .env по необходимости можно добавлять/удалять переменные окружения. Они остаются у Вас локально. Все пароли и секреты добавляются сюда.

### 3. Зависимости для ML/Backend
```bash
pip install -r requirements.txt
```
Для разработки (тесты, линтеры) дополнительно:
```bash
pip install -r requirements-dev.txt
```
requirements-dev.txt используется ТОЛЬКО для разработки. Для прода нужен чистый (без библиотечного мусора) requirements.txt.

### 3. Запуск ПО
Можно запустить без докера:
```bash
uvicorn backend.main:app --reload
```
Но лучше всегда запускать в контейнере:
```bash
docker build -f Dockerfile.cpu -t traffic-sign-backend .
docker run --env-file .env -p 8000:8000 traffic-sign-backend
# или
docker-compose up --build
```
Swagger UI: http://localhost:8000/docs

## Взаимодействие ML и Backend

- **ML‑разработчик** размещает веса модели (`.pt`) в `ml/models/` и реализует `ml/predict.py` с функцией `predict(image_path, conf)`, возвращающей список предсказаний (класс, уверенность, bbox и т.д.).
- **Backend‑разработчик** импортирует `predict` из `ml.predict` и использует её в API‑эндпоинтах.
- Модель загружается один раз при старте приложения (через `predict.py`).

## Что добавится в репозиторий

1. Донастройка Git LFS.
2. CI/CD: автоматическая сборка Docker‑образа при Pull Request (базовый GitHub Actions).
3. Контейнеризация для GPU (Dockerfile.gpu).
4. Версионирование модели и автоматическое восстановление после сбоев.
5. Настройка логирования.

Ниже предварительный `README.md` для вашего репозитория. Скопируй его, добавь в корень проекта и коммить. Далее его можно будет дополнять по мере развития проекта.

---

*Для вопросов по настройке окружения обращайтесь к @timeyann*