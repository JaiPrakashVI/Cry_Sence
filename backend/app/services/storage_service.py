from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


class StorageService:
    def __init__(self, root_dir: str) -> None:
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, upload: UploadFile) -> Path:
        suffix = Path(upload.filename or "audio.webm").suffix or ".webm"
        destination = self.root / f"{uuid4().hex}{suffix}"
        content = await upload.read()
        if not content:
            raise ValueError("Uploaded audio is empty.")
        destination.write_bytes(content)
        return destination
