"""
Функции для сохранения загруженных изображений.
"""
import aiofiles
from pathlib import Path
from typing import BinaryIO
import logging

logger = logging.getLogger(__name__)


async def save_upload_file(file_bytes: bytes, extension: str, upload_dir: str, task_id: str) -> Path:
    """
    Сохраняет байты файла в директорию upload_dir с именем {task_id}{extension}.
    Возвращает путь к сохранённому файлу.
    """
    dir_path = Path(upload_dir)
    dir_path.mkdir(parents=True, exist_ok=True)

    file_name = f"{task_id}{extension}"
    file_path = dir_path / file_name

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file_bytes)

    logger.debug("File saved", extra={"path": str(file_path)})
    return file_path