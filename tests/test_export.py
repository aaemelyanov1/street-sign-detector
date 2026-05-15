import json
import io
import csv
import pytest
import asyncio

@pytest.mark.asyncio
async def test_export_json_format(client, test_image_bytes):
    # Дождёмся результата
    files = {"file": ("test.jpg", test_image_bytes, "image/jpeg")}
    resp = await client.post("/detect", files=files, data={"confidence_threshold": "0.5"})
    task_id = resp.json()["task_id"]
    for _ in range(30):
        res = await client.get(f"/result/{task_id}")
        if res.status_code == 200 and res.json()["status"] == "completed":
            detections = res.json()["detections"]
            break
        await asyncio.sleep(1)
    else:
        pytest.fail("Не дождались результата")

    # Эмулируем создание JSON
    json_str = json.dumps(detections, indent=2)
    data = json.loads(json_str)
    assert isinstance(data, list)
    if data:
        assert "class_name" in data[0]

@pytest.mark.asyncio
async def test_export_csv_format(client, test_image_bytes):
    files = {"file": ("test.jpg", test_image_bytes, "image/jpeg")}
    resp = await client.post("/detect", files=files, data={"confidence_threshold": "0.5"})
    task_id = resp.json()["task_id"]
    for _ in range(30):
        res = await client.get(f"/result/{task_id}")
        if res.status_code == 200 and res.json()["status"] == "completed":
            detections = res.json()["detections"]
            break
        await asyncio.sleep(1)
    else:
        pytest.fail("Не дождались результата")

    # Эмулируем создание CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["class_name", "x", "y", "width", "height", "confidence"])
    for d in detections:
        writer.writerow([d["class_name"], d["bbox"][0], d["bbox"][1],
                         d["bbox"][2], d["bbox"][3], d["confidence"]])
    csv_content = output.getvalue()
    # Проверяем, что заголовок присутствует
    assert "class_name" in csv_content
    assert csv_content.count("\n") >= 1 + len(detections)