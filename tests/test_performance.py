import pytest
import time
import asyncio

# Максимально допустимое время обработки в секундах
CPU_TIME_LIMIT = 2.0
GPU_TIME_LIMIT = 0.5


async def _measure_detection_time(client, test_image_bytes) -> float:
    """Отправляет изображение и возвращает время до получения completed."""
    files = {"file": ("test.jpg", test_image_bytes, "image/jpeg")}
    data = {"confidence_threshold": "0.5"}

    start = time.monotonic()
    resp = await client.post("/detect", files=files, data=data)
    assert resp.status_code == 202
    task_id = resp.json()["task_id"]

    while True:
        elapsed = time.monotonic() - start
        if elapsed > 10.0:  # общий таймаут
            raise TimeoutError("Превышено время ожидания результата")
        result = await client.get(f"/result/{task_id}")
        if result.status_code == 200:
            data = result.json()
            if data["status"] == "completed":
                return elapsed
            elif data["status"] == "failed":
                pytest.fail(f"Задача завершилась с ошибкой: {data.get('error_message')}")
        await asyncio.sleep(0.5)


@pytest.mark.asyncio
async def test_detection_time_cpu(client, test_image_bytes):
    """Обработка на CPU должна занимать менее 2 секунд."""
    elapsed = await _measure_detection_time(client, test_image_bytes)
    assert elapsed < CPU_TIME_LIMIT, f"Обработка заняла {elapsed:.2f} сек, допустимо < {CPU_TIME_LIMIT} сек"


@pytest.mark.asyncio
async def test_detection_time_gpu(client, test_image_bytes):
    """Обработка на GPU должна занимать менее 0.5 секунд (если GPU доступен)."""
    try:
        import torch
        if not torch.cuda.is_available():
            pytest.skip("CUDA GPU недоступен")
    except ImportError:
        pytest.skip("PyTorch не установлен, GPU-тест пропущен")

    elapsed = await _measure_detection_time(client, test_image_bytes)
    assert elapsed < GPU_TIME_LIMIT, f"Обработка заняла {elapsed:.2f} сек, допустимо < {GPU_TIME_LIMIT} сек"