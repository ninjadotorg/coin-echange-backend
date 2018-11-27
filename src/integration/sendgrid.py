from django.conf import settings
from sendgrid import sendgrid, Email
from sendgrid.helpers.mail import Content, Mail, Personalization

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


def get_mock_personalization_dict(to_emails):
    """Get a dict of personalization mock."""
    mock_pers = dict()
    mock_pers['to_list'] = [Email(email) for email in to_emails]
    return mock_pers


def build_personalization(personalization):
    """Build personalization mock instance from a mock dict"""
    mock_personalization = Personalization()
    for to_addr in personalization['to_list']:
        mock_personalization.add_to(to_addr)
    return mock_personalization


@raise_api_exception(ExternalAPIException)
def send_emails(from_email, to_emails: list, subject, content, content_type='text/plain'):
    from_email = Email(from_email)

    subject = subject
    content = Content(content_type, content)
    mail = Mail(from_email, subject, None, content)

    personalization = get_mock_personalization_dict(to_emails)
    mail.add_personalization(build_personalization(personalization))

    response = client.client.mail.send.post(request_body=mail.get())
    if response.status_code > 299:
        raise Exception(response.body)
