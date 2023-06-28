from asyncio import StreamReader
from typing import Union, AsyncIterator, List, Any, Dict

from aiobotocore.client import AioBaseClient
from aiobotocore.response import StreamingBody

_MIN_PART_SIZE = 5 * (1 << 20)


class S3ObjectStorage:
    def __init__(self, client: AioBaseClient, bucket: str, key_prefix: str = ""):
        self._client = client
        self._bucket = bucket
        self.key_prefix = key_prefix

    async def _put_object(self, name: str, data: bytes) -> str:
        key = self._build_key(name)
        await self._client.put_object(Bucket=self._bucket, Key=key, Body=data)
        return key

    def _build_key(self, name: str) -> str:
        return f"{self.key_prefix}{name}"

    async def _put_large_file(self, name: str, data: AsyncIterator[bytes]) -> str:
        key = self._build_key(name)
        mpu = await self._client.create_multipart_upload(Bucket=self._bucket, Key=key)
        upload_id = mpu["UploadId"]
        parts: List[Dict[str, Any]] = []

        async for chunk in _group_chunks_to_min_part_size(data):
            if chunk == b"":
                break
            part = await self._client.upload_part(
                Bucket=self._bucket, Key=key, PartNumber=len(parts) + 1, UploadId=upload_id, Body=chunk
            )
            parts.append({"PartNumber": len(parts) + 1, "ETag": part["ETag"]})

        await self._client.complete_multipart_upload(
            Bucket=self._bucket, Key=key, UploadId=upload_id, MultipartUpload=dict(Parts=parts)
        )
        return key

    async def put_object(self, name: str, data: Union[bytes, AsyncIterator[bytes]]) -> str:
        if isinstance(data, bytes):
            return await self._put_object(name, data)
        else:
            return await self._put_large_file(name, data)

    async def stream_object(
        self, key: str, full_key: bool = False, chunk_length: int = 1024 * 1024
    ) -> AsyncIterator[bytes]:
        if full_key is False:
            key = self._build_key(key)

        response = await self._client.get_object(Bucket=self._bucket, Key=key)
        # this will ensure the connection is correctly re-used/closed
        body_stream: StreamingBody = response["Body"]
        async for chunk in body_stream.iter_chunks(chunk_length):
            yield chunk

    async def get_object(self, key: str, full_key: bool = False) -> bytes:
        if full_key is False:
            key = self._build_key(key)
        response = await self._client.get_object(Bucket=self._bucket, Key=key)
        # this will ensure the connection is correctly re-used/closed
        async with response["Body"] as stream:
            return await stream.read()

    async def list_objects(self, prefix: str = "") -> List[str]:
        objects = []
        paginator = self._client.get_paginator("list_objects_v2")
        async for result in paginator.paginate(Bucket=self._bucket, Prefix=self._build_key(prefix)):
            objects += [obj["Key"][len(self.key_prefix) :] for obj in result.get("Contents", [])]

        return objects

    async def copy_object(self, origin: str, destination: str) -> None:
        copy_source = {
            "Bucket": self._bucket,
            "Key": self._build_key(origin),
        }
        await self._client.copy_object(Bucket=self._bucket, Key=self._build_key(destination), CopySource=copy_source)

    async def delete_object(self, name):
        key = self._build_key(name)
        await self._client.delete_object(Bucket=self._bucket, Key=key)

    async def create_presigned_url(self, key_name: str, expiration: int = 3600) -> str:
        """Create a temporary public download url for the given `key_name` and `expiration` in seconds.

        Args:
            key_name (str): Full path to the object in the bucket
            expiration (int, optional): Url expiration time in seconds. Defaults to 3600.

        Returns:
            str: Download url to the object with the given expiration and key_name
        """
        return await self._client.generate_presigned_url(
            "get_object",
            Params=dict(
                Bucket=self._bucket,
                Key=key_name,
            ),
            ExpiresIn=expiration,
        )


async def _group_chunks_to_min_part_size(in_iter: AsyncIterator[bytes]) -> AsyncIterator[bytes]:
    current_chunk: bytes = b""
    async for chunk in in_iter:
        current_chunk += chunk
        if len(current_chunk) >= _MIN_PART_SIZE:
            yield current_chunk
            current_chunk = b""

    yield current_chunk
