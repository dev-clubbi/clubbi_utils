from typing import Optional, Dict, Any

from aiobotocore.client import AioBaseClient

from clubbi_utils.json import dumps

from clubbi_utils.logger import logger


class SNSPublisher:
    def __init__(self, client: AioBaseClient, topic_arn: str):
        self.topic_arn = topic_arn
        self._client = client

    async def publish(self, message: Any, attributes:  Optional[Dict[str, str]] = None) -> None:
        json_body = dumps(message)
        message_attributes = {}
        if attributes:
            message_attributes = {
                k: dict(
                    DataType='String',
                    StringValue=v,
                ) for k, v in attributes.items()
            }

        response = await self._client.publish(
            TopicArn=self.topic_arn,
            Message=json_body,
            MessageAttributes=message_attributes
        )
        logger.info(
            {
                'MessageId': response
            }
        )
