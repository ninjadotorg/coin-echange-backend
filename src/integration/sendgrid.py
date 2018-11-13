from django.conf import settings
from sendgrid import sendgrid, Email
from sendgrid.helpers.mail import Content, Mail

from common.decorators import raise_api_exception
from integration.exceptions import ExternalAPIException

client = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID['API_KEY'])


@raise_api_exception(ExternalAPIException)
def send_email(from_email, to_email, subject, content, content_type='text/plain'):
    from_email = Email(from_email)
    to_email = Email(to_email)
    subject = subject
    content = Content(content_type, content)
    mail = Mail(from_email, subject, to_email, content)
    response = client.client.mail.send.post(request_body=mail.get())

    if response.status_code > 299:
        raise Exception(response.body)
