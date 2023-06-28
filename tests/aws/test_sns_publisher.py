from unittest import IsolatedAsyncioTestCase
from uuid import uuid4

from aiobotocore.session import get_session

from clubbi_utils import json
from clubbi_utils.aws.sns_publisher import MAXIMUM_MESSAGE_LENGTH, MaximumMessageLengthError, SNSPublisher
from tests.aws.localstack_targets import create_test_client


class TestSnsPublisher(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.topic_name = str(uuid4())
        self._session = get_session()
        async with create_test_client(self._session, 'sns') as sns_client:
            topic_data = await sns_client.create_topic(
                Name=self.topic_name,
            )
        self.topic_arn = topic_data['TopicArn']

    async def test_publish(self):
        async with create_test_client(self._session, 'sns') as sns_client:
            publisher: SNSPublisher[dict] = SNSPublisher(sns_client, self.topic_arn)
            await publisher.publish({
                "teste": 2
            }, dict(a='a'))

    async def test_error_on_big_message(self):
        async with create_test_client(self._session, 'sns') as sns_client:
            publisher: SNSPublisher[dict] = SNSPublisher(sns_client, self.topic_arn)
            payload = {"teste": "a" * MAXIMUM_MESSAGE_LENGTH}
            with self.assertRaises(MaximumMessageLengthError) as e:
                await publisher.publish(payload, dict(a='a'))

            self.assertTrue(json.dumps(payload) in str(e.exception))
