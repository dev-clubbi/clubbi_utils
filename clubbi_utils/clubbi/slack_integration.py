from slack_sdk.web.async_client import AsyncWebClient

from clubbi_utils.clubbi.async_messenger import AsyncSenderStr


class SlackMessenger(AsyncSenderStr):
    def __init__(self, token: str, channel_name: str):
        self._client = AsyncWebClient(token=token)
        self._chanel_name = channel_name

    async def send(self, message: str) -> None:
        await self._client.chat_postMessage(
            channel=self._chanel_name,
            text=message,
        )