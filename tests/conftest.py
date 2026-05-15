import pytest
import httpx
import asyncio
from pathlib import Path

API_BASE_URL = "http://localhost:8000"
TEST_IMAGE_PATH = Path(__file__).parent / "test_data" / "test_image.jpg"

@pytest.fixture(scope="function")
async def client():
    """Асинхронный HTTP-клиент (создаётся заново для каждого теста)."""
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as ac:
        yield ac

@pytest.fixture(scope="function")
def test_image_bytes():
    """Содержимое тестового изображения."""
    if not TEST_IMAGE_PATH.exists():
        raise FileNotFoundError(f"Тестовое изображение не найдено: {TEST_IMAGE_PATH}")
    return TEST_IMAGE_PATH.read_bytes()

@pytest.fixture(scope="function")
def test_image_path():
    return TEST_IMAGE_PATH