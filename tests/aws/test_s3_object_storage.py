from typing import AsyncIterator
from unittest import IsolatedAsyncioTestCase
import asyncio
import aiobotocore
from clubbi_utils.aws.s3_object_storage import S3ObjectStorage
from tests.aws.localstack_targets import create_test_client

BUCKET_NAME = "test-bucket"
PREFIX=""

class TestS3ObjectStorage(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        super().setUp()    
        self._session = aiobotocore.get_session()
        await self._remove_objects()
    
    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()
        await self._remove_objects()
    
    async def _remove_objects(self):
        async with create_test_client(self._session, 's3') as client:
            paginator = client.get_paginator('list_objects')
            key_to_delete = []
            async for result in paginator.paginate(Bucket=BUCKET_NAME, Prefix=PREFIX):
                for content in result.get('Contents', []):
                    key_to_delete.append(content["Key"])
            if key_to_delete:
                delete_payload = dict(Objects=[dict(Key=key) for key in key_to_delete])
                await client.delete_objects(Bucket=BUCKET_NAME,  Delete=delete_payload)
    
    async def test_put_get_small_file(self):
        async with create_test_client(self._session, 's3') as client:
            storage = S3ObjectStorage(client, BUCKET_NAME)
            key = await storage.put_object("small_file.txt", b"hello world")
            file = await storage.get_object("small_file.txt")

            self.assertEqual(key, "small_file.txt")
            self.assertEqual(file, b"hello world")
    
    async def test_put_large_file(self):
        async def byte_iterator()->AsyncIterator[bytes]:
            yield b"large "
            yield b"hello "
            yield b"world"
        async with create_test_client(self._session, 's3') as client:
            storage = S3ObjectStorage(client, BUCKET_NAME)
            key = await storage.put_object("large_file.txt", byte_iterator())
            file = await storage.get_object("large_file.txt")

            self.assertEqual(key, "large_file.txt")
            self.assertEqual(file, b"large hello world")
    
    async def test_read_large_file(self):
        async with create_test_client(self._session, 's3') as client:
            storage = S3ObjectStorage(client, BUCKET_NAME)
            key = await storage.put_object("read_large_file.txt", b"helloworld")
            chunks = []
            async for chunk in storage.stream_object("read_large_file.txt", chunk_length=3):
                chunks.append(chunk)
            self.assertEqual(key, "read_large_file.txt")
            self.assertEqual(chunks, [b"hel", b"low", b"orl", b"d"])
    
    async def test_copy_object(self):
        async with create_test_client(self._session, 's3') as client:
            storage = S3ObjectStorage(client, BUCKET_NAME)
            await storage.put_object("file_to_be_copied.txt", data=b"to be copied")
            await storage.copy_object("file_to_be_copied.txt", "file_copied.txt")

            file_to_be_copied = await storage.get_object("file_to_be_copied.txt")
            file_copied = await storage.get_object("file_copied.txt")

            self.assertEqual(file_to_be_copied, b"to be copied")
            self.assertEqual(file_copied, file_to_be_copied)
    
    async def test_list_objects(self):
        async with create_test_client(self._session, 's3') as client:
            storage = S3ObjectStorage(client, BUCKET_NAME)
            
            file_names = [f"folder/file{i}.txt" for i in range(10)]
            
            await asyncio.gather(*(storage.put_object(fname, data=b"content")for fname in file_names))

            files = await storage.list_objects("folder")

            self.assertEqual(files, file_names)
