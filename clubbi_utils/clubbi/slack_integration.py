import os
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

client = AsyncWebClient(token=os.environ["SLACK_BOT_TOKEN"])


async def slack_it(channel_name: str, message: str) -> None:
    try:
        await client.chat_postMessage(channel=channel_name, text=message)
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]
        print(f"Got an error: {e.response['error']}")
