from typing import AsyncIterator
from unittest import IsolatedAsyncioTestCase
import asyncio

from clubbi_utils.aws.local_mocks.s3_object_storage_local_mock import (
    S3ObjectStorageLocalMock,
)
from pathlib import Path


class TestS3ObjectStorageLocalMock(IsolatedAsyncioTestCase):
    async def test_path(self):
        storage = S3ObjectStorageLocalMock()

        name = str(storage.path).split("-")[-1]
        self.assertEqual(name, "S3ObjectStorageLocalMock")

        storage = S3ObjectStorageLocalMock(name="test")
        name = str(storage.path).split("-")[-1]
        self.assertEqual(name, "test")

    async def test_put_get_small_file(self):
        storage = S3ObjectStorageLocalMock()
        key = await storage.put_object("small_file.txt", b"hello world")
        file = await storage.get_object("small_file.txt")

        self.assertEqual(key, "small_file.txt")
        self.assertEqual(file, b"hello world")
        self.assertEqual(Path(storage.path, "small_file.txt").read_bytes(), file)

    async def test_put_large_file(self):
        async def byte_iterator() -> AsyncIterator[bytes]:
            yield b"large "
            yield b"hello "
            yield b"world"

        storage = S3ObjectStorageLocalMock()
        key = await storage.put_object("large_file.txt", byte_iterator())
        file = await storage.get_object("large_file.txt")
        self.assertEqual(key, "large_file.txt")
        self.assertEqual(file, b"large hello world")
        self.assertEqual(Path(storage.path, "large_file.txt").read_bytes(), file)

    async def test_read_large_file(self):
        storage = S3ObjectStorageLocalMock()
        key = await storage.put_object("read_large_file.txt", b"helloworld")
        chunks = []
        async for chunk in storage.stream_object("read_large_file.txt", chunk_length=3):
            chunks.append(chunk)
        self.assertEqual(key, "read_large_file.txt")
        self.assertEqual(chunks, [b"hel", b"low", b"orl", b"d"])

    async def test_copy_object(self):
        storage = S3ObjectStorageLocalMock()
        await storage.put_object("file_to_be_copied.txt", data=b"to be copied")
        await storage.copy_object("file_to_be_copied.txt", "file_copied.txt")

        file_to_be_copied = await storage.get_object("file_to_be_copied.txt")
        file_copied = await storage.get_object("file_copied.txt")

        self.assertEqual(file_to_be_copied, b"to be copied")
        self.assertEqual(file_copied, file_to_be_copied)
        self.assertEqual(
            Path(storage.path, "file_to_be_copied.txt").read_bytes(),
            Path(storage.path, "file_copied.txt").read_bytes(),
        )

    async def test_list_objects(self):
        storage = S3ObjectStorageLocalMock()

        self.assertEqual(await storage.list_objects("folder"), [])
        file_names = [f"folder/file{i}.txt" for i in range(10)]

        await asyncio.gather(
            *(storage.put_object(fname, data=b"content") for fname in file_names)
        )

        files = await storage.list_objects("folder")

        self.assertEqual(sorted(files), sorted(file_names))
