from datetime import timedelta

from django.conf import settings
from django.db.models import Q, F

from coin_exchange.constants import ORDER_TYPE, ORDER_STATUS
from coin_exchange.models import Order
from coin_system.constants import CACHE_KEY_SYSTEM_REMINDER, CACHE_KEY_SYSTEM_NOTIFICATION
from coin_user.constants import VERIFICATION_LEVEL, VERIFICATION_STATUS
from coin_user.models import ExchangeUser
from common.business import get_now
from common.constants import DIRECTION
from common.decorators import raise_api_exception, cache_first
from common.exceptions import UnexpectedException
from notification.constants import NOTIFICATION_METHOD, NOTIFICATION_GROUP
from notification.models import SystemNotification, SystemReminder, SystemReminderAction
from notification.provider.email import EmailNotification
from notification.provider.slack import SlackNotification
from notification.provider.sms import SmsNotification


@raise_api_exception(UnexpectedException)
@cache_first(CACHE_KEY_SYSTEM_REMINDER, timeout=5 * 60)
def get_system_reminder(group) -> list:
    objs = SystemReminder.objects.filter(group=group, active=True)
    return [obj for obj in objs]


@raise_api_exception(UnexpectedException)
@cache_first(CACHE_KEY_SYSTEM_NOTIFICATION, timeout=5 * 60)
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
            order_page = 'order'

        order_link = settings.FRONTEND_HOST + '/admin/coin_exchange/' + order_page + '/?q=' + order_data['ref_code']
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


class ComparePriceNotification(object):
    @staticmethod
    def send_new_compare_price_notification(compare_data: dict):
        msg = ''
        title = ''
        if settings.TEST:
            msg = 'TEST - '
            title = 'TEST - '

        msg += '[COMPARE-PRICE] We have high rate of {} with CoinCap at rate usd is {}, please check our prices'.format(
            compare_data['symbol'],
            compare_data['rateUsd'],
        )
        title += '[COMPARE-PRICE] We have high rate detected!'

        content = {
            'subject': title,
            'content': msg,
        }

        notifications = get_system_notification(NOTIFICATION_GROUP.compare_price)
        for notification in notifications:
            NotificationManagement.send_notification(notification, **content)


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


class ReminderManagement(object):
    @staticmethod
    def get_action_to_do():
        reminder_actions = SystemReminderAction.objects.all()
        actions = []

        # order_action = verification_action = None
        pending_order = ReminderManagement.check_pending_order()
        pending_verification = ReminderManagement.check_pending_verification()

        reminder_groups = {
            NOTIFICATION_GROUP.order: {
                'group': NOTIFICATION_GROUP.order,
                'pending': pending_order,
            },
            NOTIFICATION_GROUP.notification: {
                'group': NOTIFICATION_GROUP.notification,
                'pending': pending_verification,
            }
        }

        # If there are current actions
        for reminder_action in reminder_actions:
            # No pending anymore
            if not reminder_groups[reminder_action.reminder.group]['pending']:
                reminder_action.delete()

            # Check if the action is not at on hold
            if reminder_action.updated_at + timedelta(seconds=60 * reminder_action.stop_duration) < get_now():
                # Check if the action still have active time
                if reminder_action.active_time:
                    # Check if the time is proper to do?
                    if reminder_action.updated_at + timedelta(
                            seconds=60 * reminder_action.reminder.frequency) < get_now():
                        reminder_action.active_time = F('active_time') - 1
                        reminder_action.save()
                        actions.append(reminder_action)
                else:
                    # Not, go next
                    # Check if the time is proper to do?
                    if reminder_action.updated_at + timedelta(
                            seconds=60 * reminder_action.reminder.break_duration) < get_now():

                        reminder = ReminderManagement.get_next_reminder(reminder_action.group,
                                                                        reminder_action.reminder.id)

                        reminder_action.reminder = reminder
                        reminder_action.active_time = reminder.times
                        reminder.save()
                        actions.append(reminder_action)
            elif reminder_action.stop_duration:
                # Time out of stop duration
                # Just delete and the code below will add again to reset the action if needed
                reminder_action.delete()

        # There is no action, make one
        if not actions:
            for key, item in reminder_groups.items():
                if item['pending']:
                    reminder = ReminderManagement.get_next_reminder(key)
                    if reminder:
                        action = SystemReminderAction.objects.create(
                            group=key,
                            active_reminder=reminder,
                            active_time=reminder.times - 1,
                            stop_duration=0,
                        )
                        actions.append(action)

        return actions

    @staticmethod
    def do_reminder():
        pass

    @staticmethod
    def get_next_reminder(group, reminder_id: int = 0) -> SystemReminder:
        reminders = get_system_reminder(group)
        reminder = None
        if not reminders:
            if not reminder_id:
                return reminders[0]
            else:
                find_next = False
                for reminder in reminders:
                    if find_next:
                        return reminder
                    if reminder.id == reminder_id:
                        find_next = True
        return reminder

    @staticmethod
    def check_pending_order():
        # Check if there pending things to notify
        pending_order = Order.objects.filter(
            (Q(direction=DIRECTION.buy) & Q(order_type=ORDER_TYPE.cod) &
             Q(status=ORDER_STATUS.pending)) |
            (Q(direction=DIRECTION.buy) & Q(order_type=ORDER_TYPE.bank) &
             Q(status=ORDER_STATUS.fiat_transferring)) |
            (Q(direction=DIRECTION.sell) & Q(order_type=ORDER_TYPE.cod) &
             Q(status=ORDER_STATUS.transferring))
        ).exists()
        return pending_order

    @staticmethod
    def check_pending_verification():
        pending_verification = ExchangeUser.objects.filter(
            verification_status=VERIFICATION_STATUS.pending,
            verification_level__gt=VERIFICATION_LEVEL.level_2).exists()
        return pending_verification
