from typing import AsyncIterator, List, Union
from clubbi_utils.logging import logger

from pathlib import Path
import tempfile
import shutil


class S3ObjectStorageLocalMock:
    def __init__(self, name: str = "S3ObjectStorageLocalMock", key_prefix: str = ""):
        self._key_prefix = key_prefix
        self._path = Path(tempfile.TemporaryDirectory().name + "-" + name, key_prefix)
        self._path.mkdir(parents=True)
        logger.info(f"initializing S3ObjectStorageLocalMock in {self.path}")

    def __del__(self):
        shutil.rmtree(self._path)

    @property
    def path(self) -> Path:
        return self._path

    async def put_object(
        self,
        name: str,
        data: Union[bytes, AsyncIterator[bytes]],
    ) -> str:
        file_path = Path(self.path, name)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, bytes):
            file_path.write_bytes(data)
            return name
        with file_path.open("wb") as f:
            async for chunk in data:
                f.write(chunk)
        return name

    async def stream_object(
        self,
        key: str,
        full_key: bool = False,
        chunk_length: int = 1024 * 1024,
    ) -> AsyncIterator[bytes]:
        file_path = Path(self.path, key)
        with file_path.open("rb") as f:
            while chunk := f.read(chunk_length):
                yield chunk

    async def get_object(self, key: str, full_key: bool = False) -> bytes:
        file_path = Path(self.path, key)
        return file_path.read_bytes()

    async def list_objects(self, prefix: str = "") -> List[str]:
        dir_path = Path(self.path, prefix)
        return [str(p.relative_to(self.path)) for p in dir_path.glob("*")]

    async def copy_object(self, origin: str, destination: str) -> None:
        origin_path = Path(self.path, origin)
        destination_path = Path(self.path, destination)

        shutil.copy(origin_path, destination_path)
