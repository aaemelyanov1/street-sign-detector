import pytest
import asyncio
from typing import List, Dict

@pytest.mark.asyncio
class TestDetectionWorkflow:

    async def _submit_and_wait(self, client, image_bytes, confidence=0.5) -> List[Dict]:
        files = {"file": ("test.jpg", image_bytes, "image/jpeg")}
        data = {"confidence_threshold": str(confidence)}
        resp = await client.post("/detect", files=files, data=data)
        assert resp.status_code == 202
        task_id = resp.json()["task_id"]

        # Ожидание завершения
        for _ in range(30):
            result = await client.get(f"/result/{task_id}")
            assert result.status_code == 200
            result_data = result.json()
            if result_data["status"] == "completed":
                return result_data.get("detections") or []
            elif result_data["status"] == "failed":
                pytest.fail(f"Задача завершилась с ошибкой: {result_data.get('error_message')}")
            await asyncio.sleep(1)
        pytest.fail("Таймаут ожидания завершения задачи")

    async def test_detections_structure(self, client, test_image_bytes):
        detections = await self._submit_and_wait(client, test_image_bytes)
        assert isinstance(detections, list)
        if len(detections) > 0:
            for det in detections:
                assert "class_name" in det
                assert "bbox" in det
                assert "confidence" in det
                assert isinstance(det["bbox"], list) and len(det["bbox"]) == 4
                assert 0.0 <= det["confidence"] <= 1.0

    async def test_confidence_threshold(self, client, test_image_bytes):
        # С высоким порогом должны получить меньше или столько же детекций, сколько с низким
        detections_low = await self._submit_and_wait(client, test_image_bytes, 0.1)
        detections_high = await self._submit_and_wait(client, test_image_bytes, 0.9)
        # Логично, что len(detections_high) <= len(detections_low)
        assert len(detections_high) <= len(detections_low)

    async def test_bbox_format(self, client, test_image_bytes):
        detections = await self._submit_and_wait(client, test_image_bytes)
        if detections:
            for det in detections:
                x, y, w, h = det["bbox"]
                # Простейшая проверка: ширина и высота положительные
                assert w > 0
                assert h > 0