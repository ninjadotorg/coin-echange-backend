from django.conf import settings

from content.models import EmailContent
from integration.sendgrid import send_email, send_emails


class EmailNotification(object):
    @staticmethod
    def send_simple_email(to_email: str, subject: str, content: str, raise_exception: bool = False):
        try:
            send_email(settings.EMAIL_FROM_ADDRESS, to_email, subject, content)
        except Exception:
            if raise_exception:
                raise

    @staticmethod
    def send_simple_emails(to_emails: list, subject: str, content: str, raise_exception: bool = False):
        try:
            send_emails(settings.EMAIL_FROM_ADDRESS, to_emails, subject, content)
        except Exception:
            if raise_exception:
                raise

    @staticmethod
    def send_email(to_email: str, subject: str, content: str, raise_exception: bool = False):
        try:
            send_email(settings.EMAIL_FROM_ADDRESS, to_email, subject, content, content_type='text/html')
        except Exception:
            if raise_exception:
                raise

    @staticmethod
    def send_email_template(to_email: str, content_key: str, language: str, params: dict = None,
                            raise_exception: bool = False):
        obj = EmailContent.objects.get(purpose=content_key, language=language)
        content = obj.content
        if params:
            content = content.format(**params)
        EmailNotification.send_email(to_email, obj.subject, content, raise_exception)
