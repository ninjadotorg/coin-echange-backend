from django.conf import settings
from twilio.rest import Client

from common.decorators import raise_api_exception
from integration.exceptions import ExternalAPIException

client = Client(settings.TWILIO['API_SID'], settings.TWILIO['API_AUTH_TOKEN'])


@raise_api_exception(ExternalAPIException)
def send_sms(from_phone: str, to_phone: str, message: str):
    client.messages.create(
        from_=from_phone,
        body=message,
        to=to_phone
    )
