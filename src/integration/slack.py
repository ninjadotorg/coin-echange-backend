from django.conf import settings
from slackclient import SlackClient

from common.decorators import raise_api_exception
from integration.exceptions import ExternalAPIException

client = SlackClient(settings.SLACK['TOKEN'])


@raise_api_exception(ExternalAPIException)
def send_slack(channel: str, message: str):
    result = client.api_call(
        "chat.postMessage",
        channel=channel,
        text=message
    )
    if not result['ok']:
        raise Exception(result)
