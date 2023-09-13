from datetime import datetime, timedelta
from typing import AsyncIterator
from unittest import IsolatedAsyncioTestCase
import asyncio
from aiobotocore.session import get_session
from dateutil.tz import tzutc
from clubbi_utils.aws.s3_object_storage import S3ObjectStorage
from tests.aws.localstack_targets import create_test_client
from aiobotocore.client import AioBaseClient
import http.client
from urllib.parse import urlparse

BUCKET_NAME = "test-bucket"
PREFIX = ""


class TestS3ObjectStorage(IsolatedAsyncioTestCase):
    async def _yield_s3_client(self) -> AsyncIterator[AioBaseClient]:
        async with create_test_client(self._session, "s3") as s3_client:
            yield s3_client

    def _get_request_http(self, url: str) -> bytes:
        parsed_url = urlparse(url)
        conn = http.client.HTTPConnection(f"{parsed_url.hostname}:{parsed_url.port}")
        conn.request("GET", parsed_url.path)
        return conn.getresponse().read()

    async def asyncSetUp(self) -> None:
        super().setUp()
        self._session = get_session()
        self._s3_client_aiter = self._yield_s3_client()
        self._client = await self._s3_client_aiter.__anext__()
        await self._client.create_bucket(
            ACL="private",
            Bucket=BUCKET_NAME,
        )
        self._storage = S3ObjectStorage(self._client, BUCKET_NAME)
        await self._remove_objects()

    async def asyncTearDown(self) -> None:
        await self._remove_objects()
        await self._client.delete_bucket(Bucket=BUCKET_NAME)
        with self.assertRaises(StopAsyncIteration):
            await self._s3_client_aiter.__anext__()
        await super().asyncTearDown()

    async def _remove_objects(self):
        paginator = self._client.get_paginator("list_objects")
        key_to_delete = []
        async for result in paginator.paginate(Bucket=BUCKET_NAME, Prefix=PREFIX):
            for content in result.get("Contents", []):
                key_to_delete.append(content["Key"])
        if key_to_delete:
            delete_payload = dict(Objects=[dict(Key=key) for key in key_to_delete])
            await self._client.delete_objects(Bucket=BUCKET_NAME, Delete=delete_payload)

    async def test_put_get_small_file(self):
        key = await self._storage.put_object("small_file.txt", b"hello world")
        file = await self._storage.get_object("small_file.txt")

        self.assertEqual(key, "small_file.txt")
        self.assertEqual(file, b"hello world")

    async def test_put_large_file(self):
        async def byte_iterator() -> AsyncIterator[bytes]:
            yield b"large "
            yield b"hello "
            yield b"world"

        key = await self._storage.put_object("large_file.txt", byte_iterator())
        file = await self._storage.get_object("large_file.txt")

        self.assertEqual(key, "large_file.txt")
        self.assertEqual(file, b"large hello world")

    async def test_read_large_file(self):
        key = await self._storage.put_object("read_large_file.txt", b"helloworld")
        chunks = []
        async for chunk in self._storage.stream_object("read_large_file.txt", chunk_length=3):
            chunks.append(chunk)
        self.assertEqual(key, "read_large_file.txt")
        self.assertEqual(chunks, [b"hel", b"low", b"orl", b"d"])

    async def test_copy_object(self):
        await self._storage.put_object("file_to_be_copied.txt", data=b"to be copied")
        await self._storage.copy_object("file_to_be_copied.txt", "file_copied.txt")

        file_to_be_copied = await self._storage.get_object("file_to_be_copied.txt")
        file_copied = await self._storage.get_object("file_copied.txt")

        self.assertEqual(file_to_be_copied, b"to be copied")
        self.assertEqual(file_copied, file_to_be_copied)

    async def test_list_objects(self):
        self.assertEqual(await self._storage.list_objects("folder"), [])

        file_names = [f"folder/file{i}.txt" for i in range(10)]

        await asyncio.gather(*(self._storage.put_object(fname, data=b"content") for fname in file_names))

        files = await self._storage.list_objects("folder")

        self.assertEqual(files, file_names)

    async def test_create_presigned_url(self):
        key = await self._storage.put_object("file.txt", b"hello world")
        link = await self._storage.create_presigned_url(key, expiration=3600)
        self.assertEqual(self._get_request_http(link), b"hello world")

    async def test_get_object_attribute(self) -> None:
        now = datetime.utcnow().replace(tzinfo=tzutc())
        key = await self._storage.put_object("file.txt", b"hello world")
        info = await self._storage.get_object_attributes(key)
        self.assertEqual(info.object_size, len(b"hello world"))
        self.assertTrue(
            now - timedelta(seconds=2) <= info.last_modified <= now + timedelta(seconds=2), (info.last_modified, now)
        )
