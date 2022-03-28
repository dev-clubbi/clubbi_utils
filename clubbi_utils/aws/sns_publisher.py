from typing import Optional, Dict, TypeVar, Generic

from aiobotocore.client import AioBaseClient

from clubbi_utils.json import dumps
from clubbi_utils.logging import logger

# docs: https://aws.amazon.com/sns/faqs/
MAXIMUM_MESSAGE_LENGTH = 256_000


class MaximumMessageLengthError(RuntimeError):
    pass


E = TypeVar("E")


class SNSPublisher(Generic[E]):
    def __init__(self, client: AioBaseClient, topic_arn: str):
        self.topic_arn = topic_arn
        self._client = client

    async def publish(
        self, message: E, attributes: Optional[Dict[str, str]] = None, message_group_id: Optional[str] = None
    ) -> None:
        json_body = dumps(message)
        if len(json_body) > MAXIMUM_MESSAGE_LENGTH:
            err_msg = f"The following message is larger than the maximum message size({MAXIMUM_MESSAGE_LENGTH}): '{json_body}'"
            raise MaximumMessageLengthError(err_msg)
        message_attributes = {}
        if attributes:
            message_attributes = {
                k: dict(
                    DataType="String",
                    StringValue=v,
                )
                for k, v in attributes.items()
            }

        publish_kwargs = dict(TopicArn=self.topic_arn, Message=json_body, MessageAttributes=message_attributes)
        if message_group_id is not None:
            publish_kwargs["MessageGroupId"] = message_group_id
        response = await self._client.publish(**publish_kwargs)
        logger.info({"MessageId": response})
