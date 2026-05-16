import pytest
import asyncio

@pytest.mark.asyncio
class TestHealthEndpoints:

    async def test_health(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    async def test_ready(self, client):
        response = await client.get("/ready")
        assert response.status_code == 200
        # Содержимое не регламентировано, но статус 200 обязателен

@pytest.mark.asyncio
class TestDetectEndpoint:

    async def test_post_detect_with_valid_image(self, client, test_image_bytes):
        files = {"file": ("test.jpg", test_image_bytes, "image/jpeg")}
        data = {"confidence_threshold": 0.5}
        response = await client.post("/detect", files=files, data=data)
        assert response.status_code == 202
        json_resp = response.json()
        assert "task_id" in json_resp
        assert "status_url" in json_resp

    async def test_post_detect_with_invalid_format(self, client):
        files = {"file": ("test.txt", b"fake data", "text/plain")}
        response = await client.post("/detect", files=files)
        assert response.status_code == 400

    async def test_post_detect_with_large_file(self, client):
        # Создаём файл больше 30 МБ
        big_data = b"x" * (31 * 1024 * 1024)
        files = {"file": ("large.jpg", big_data, "image/jpeg")}
        response = await client.post("/detect", files=files)
        # Ограничение размера теперь на стороне nginx, API принимает любой размер
        assert response.status_code == 202

@pytest.mark.asyncio
class TestResultEndpoint:

    @pytest.fixture
    async def existing_task_id(self, client, test_image_bytes):
        files = {"file": ("test.jpg", test_image_bytes, "image/jpeg")}
        resp = await client.post("/detect", files=files)
        assert resp.status_code == 202
        return resp.json()["task_id"]

    async def test_get_result_not_found(self, client):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/result/{fake_id}")
        assert response.status_code == 404

    async def test_get_result_valid(self, client, existing_task_id):
        # Ждём завершения (максимум 30 секунд)
        for _ in range(30):
            resp = await client.get(f"/result/{existing_task_id}")
            assert resp.status_code == 200
            data = resp.json()
            if data["status"] in ("completed", "failed"):
                break
            await asyncio.sleep(1)
        else:
            pytest.fail("Таймаут ожидания результата")