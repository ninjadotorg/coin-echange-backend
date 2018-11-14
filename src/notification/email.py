from django.conf import settings

from integration.sendgrid import send_email


class EmailNotification(object):
    @staticmethod
    def send_simple_email():
        pass

    @staticmethod
    def send_email(to_email: str, subject: str, content: str, raise_exception: False):
        try:
            send_email(settings.EMAIL_FROM_ADDRESS, to_email, subject, content)
        except Exception:
            if raise_exception:
                raise
