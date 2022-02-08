from clubbi_utils.common.async_messenger import AsyncSenderStr
from slack_sdk.web.async_client import AsyncWebClient


class SlackMessenger(AsyncSenderStr):
    def __init__(self, token: str, channel_name: str):
        self._client = AsyncWebClient(token=token)
        self._channel_name = channel_name

    async def send(self, message: str) -> None:
        await self._client.chat_postMessage(
            channel=self._channel_name,
            text=message,
        )