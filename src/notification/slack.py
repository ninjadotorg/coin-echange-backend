from django.conf import settings

from integration.slack import send_slack


class SlackNotification(object):
    @staticmethod
    def send(message: str, raise_exception=False):
        try:
            send_slack(settings.SLACK_CHANNEL, message)
        except Exception:
            if raise_exception:
                raise
