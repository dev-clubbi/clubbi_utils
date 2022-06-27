from typing import TypeVar, Callable, Awaitable, Any, Optional

from pydantic import BaseSettings

from clubbi_utils.common.async_messenger import AsyncSenderStr
from slack_sdk.web.async_client import AsyncWebClient

from clubbi_utils.logger import logger

RT = TypeVar("RT")


class SlackMessenger(AsyncSenderStr):
    def __init__(self, token: str, channel_name: str):
        self._client = AsyncWebClient(token=token)
        self._channel_name = channel_name

    async def send(self, message: str) -> None:
        await self._client.chat_postMessage(
            channel=self._channel_name,
            text=message,
        )

    async def send_message_as_file(self, content: str, file_name: Optional[str], title: Optional[str],
                                   message: Optional[str]) -> None:
        await self._client.files_upload(channels=self._channel_name,
                                        content=content,
                                        filename=file_name,
                                        title=title,
                                        initial_comment=message)


class SlackSettings(BaseSettings):
    environment: str
    slack_channel_name: str = ""
    slack_token: str = ""


class LocalLoggerMessager(AsyncSenderStr):
    @staticmethod
    async def send(message: str) -> None:
        logger.info(f"LoggerMessager: {message}")


def with_slack_messenger(f: Callable[..., Awaitable[RT]]) -> Callable[..., Awaitable[RT]]:
    async def wrapper(*args: Any, **kwargs: Any) -> RT:
        settings = SlackSettings()
        slack_messenger: AsyncSenderStr

        if settings.environment == "local":
            slack_messenger = LocalLoggerMessager()
        else:
            assert settings.slack_token and settings.slack_channel_name
            slack_messenger = SlackMessenger(settings.slack_token, settings.slack_channel_name)
        return await f(slack_messenger, *args, **kwargs)

    return wrapper
