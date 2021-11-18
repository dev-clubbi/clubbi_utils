from unittest import IsolatedAsyncioTestCase
from uuid import uuid4

import aiobotocore

from clubbi.aws.sns_publisher import SNSPublisher
from tests.aws.localstack_targets import create_test_client


class TestSnsPublisher(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.topic_name = str(uuid4())
        self._session = aiobotocore.get_session()
        async with create_test_client(self._session, 'sns') as sns_client:
            topic_data = await sns_client.create_topic(
                Name=self.topic_name,
            )
        self.topic_arn = topic_data['TopicArn']

    async def test_publish(self):
        async with create_test_client(self._session, 'sns') as sns_client:
            publisher = SNSPublisher(sns_client, self.topic_arn)
            await publisher.publish({
                "teste": 2
            }, dict(a='a'))
