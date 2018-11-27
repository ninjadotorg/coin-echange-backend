import requests
from django.conf import settings

from coin_exchange.constants import ORDER_TYPE
from coin_exchange.models import Order
from coin_system.business import send_email_notification, send_slack_notification, send_sms_notification
from coin_system.constants import NOTIFICATION_METHOD
from coin_system.models import SystemNotification
from common.constants import DIRECTION


class NotificationManagement(object):
    @staticmethod
    def send_new_order_request(order: Order):
        url = settings.EXCHANGE_API + '/new-order-notification/'
        try:
            requests.post(url, data={
                'order_type': order.order_type,
                'direction': order.direction,
                'ref_code': order.ref_code,
                'id': order.id,
            }, headers={'Content-type': 'application/json'}, timeout=200)
        except Exception:
            pass

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

        notifications = SystemNotification.objects.filter(active=True)
        for notification in notifications:
            if notification.method == NOTIFICATION_METHOD.email:
                send_email_notification(notification, msg, email_content)
            elif notification.method == NOTIFICATION_METHOD.slack:
                send_slack_notification(notification, slack_content)
            elif notification.method == NOTIFICATION_METHOD.sms:
                send_sms_notification(notification, msg)
