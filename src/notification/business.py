from django.conf import settings

from coin_exchange.constants import ORDER_TYPE
from coin_system.constants import CACHE_KEY_SYSTEM_REMINDER, CACHE_KEY_SYSTEM_NOTIFICATION
from coin_user.constants import VERIFICATION_LEVEL
from common.constants import DIRECTION
from common.decorators import raise_api_exception, cache_first
from common.exceptions import UnexpectedException
from notification.constants import NOTIFICATION_METHOD, NOTIFICATION_GROUP
from notification.models import SystemNotification, SystemReminder
from notification.provider.email import EmailNotification
from notification.provider.slack import SlackNotification
from notification.provider.sms import SmsNotification


@raise_api_exception(UnexpectedException)
@cache_first(CACHE_KEY_SYSTEM_REMINDER, timeout=5*60)
def get_system_reminder() -> list:
    objs = SystemReminder.objects.filter(active=True)
    return [obj for obj in objs]


@raise_api_exception(UnexpectedException)
@cache_first(CACHE_KEY_SYSTEM_NOTIFICATION, timeout=5*60)
def get_system_notification(group) -> list:
    objs = SystemNotification.objects.filter(group=group, active=True)
    return [obj for obj in objs]


class NotificationManagement(object):
    @staticmethod
    def send_notification(notification: SystemNotification, **kwargs):
        if notification.method == NOTIFICATION_METHOD.email:
            NotificationManagement.send_email_notification(notification, kwargs['subject'], kwargs['content'])
        elif notification.method == NOTIFICATION_METHOD.slack:
            NotificationManagement.send_slack_notification(notification, kwargs['content'])
        elif notification.method == NOTIFICATION_METHOD.sms:
            NotificationManagement.send_sms_notification(notification, kwargs['content'])

    @staticmethod
    def send_email_notification(notification: SystemNotification, subject: str, content: str):
        emails = [email.strip() for email in notification.target.split(';')]
        EmailNotification.send_simple_emails(emails, subject, content)

    @staticmethod
    def send_slack_notification(notification: SystemNotification, content):
        SlackNotification.send_channel(notification.target, content)

    @staticmethod
    def send_sms_notification(notification: SystemNotification, content):
        to_phones = [phone.strip() for phone in notification.target.split(';')]
        for to_phone in to_phones:
            SmsNotification.send_sms(to_phone, content)


class OrderNotification(object):
    @staticmethod
    def send_new_order_notification(order_data: dict):
        msg = ''
        if settings.TEST:
            msg = 'TEST - '

        msg += '[ORDER] [{}] You have a new {} order, please check ref code: {}'.format(
            order_data['order_type'].upper(),
            order_data['direction'].upper(),
            order_data['ref_code'],
        )

        email_template = '''Click here to view the Order #{} - {}'''

        if order_data['direction'] == DIRECTION.sell:
            order_page = 'sellingorder'
        else:
            if order_data['order_type'] == ORDER_TYPE.cod:
                order_page = 'codorder'
            else:
                order_page = 'order'

        order_link = settings.FRONTEND_HOST + '/admin/' + order_page + '/?q=' + order_data['ref_code']
        email_content = email_template.format(order_data['id'], order_link)

        slack_content = msg + '\n' + 'Click here to view the Order #{} - {}'.format(order_data['id'], order_link)

        notifications = get_system_notification(NOTIFICATION_GROUP.order)
        for notification in notifications:
            if notification.method == NOTIFICATION_METHOD.email:
                NotificationManagement.send_email_notification(notification, msg, email_content)
            elif notification.method == NOTIFICATION_METHOD.slack:
                NotificationManagement.send_slack_notification(notification, slack_content)
            elif notification.method == NOTIFICATION_METHOD.sms:
                NotificationManagement.send_sms_notification(notification, msg)


class UserVerificationNotification(object):
    @staticmethod
    def send_user_verification_notification(user_data: dict):
        msg = ''
        if settings.TEST:
            msg = 'TEST - '

        msg += '[VERIFY] Please approve this account User #{} - Upgrading {}'.format(
            user_data['id'],
            VERIFICATION_LEVEL[user_data['level']],
        )

        email_template = '''Click here to view the User #{} - {}'''
        user_link = settings.FRONTEND_HOST + '/admin/coin_user/exchangeuser/?q=' + user_data['name']
        email_content = email_template.format(user_data['id'], user_link)

        slack_content = msg + '\n' + 'Click here to view {}'.format(user_link)

        notifications = get_system_notification(NOTIFICATION_GROUP.verification)
        for notification in notifications:
            if notification.method == NOTIFICATION_METHOD.email:
                NotificationManagement.send_email_notification(notification, msg, email_content)
            elif notification.method == NOTIFICATION_METHOD.slack:
                NotificationManagement.send_slack_notification(notification, slack_content)
            elif notification.method == NOTIFICATION_METHOD.sms:
                NotificationManagement.send_sms_notification(notification, msg)
