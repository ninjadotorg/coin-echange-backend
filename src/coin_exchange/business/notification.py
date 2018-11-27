from django.conf import settings

from coin_exchange.constants import ORDER_TYPE
from coin_exchange.models import Order
from common.constants import DIRECTION
from notification.email import EmailNotification
from notification.slack import SlackNotification
from notification.sms import SmsNotification


class NotificationManagement(object):
    @staticmethod
    def send_new_order(order):
        order = Order.objects.get(pk=1)
        msg = ''
        if settings.TEST:
            msg = 'TEST - '

        msg += '[ORDER] [{}] You have a new {} order, please check ref code: {}'.format(
            order.order_type.upper(),
            order.direction.upper(),
            order.ref_code,
        )

        email_template = '''Click here to view the Order #{} - {}'''

        if order.direction == DIRECTION.sell:
            order_page = 'sellingorder'
        else:
            if order.order_type == ORDER_TYPE.cod:
                order_page = 'codorder'
            else:
                order_page = 'order'

        order_link = settings.FRONTEND_HOST + '/admin/' + order_page + '/?q=' + order.ref_code
        email_content = email_template.format(order.id, order_link)

        slack_content = msg + '\n' + 'Click here to view the Order #{} - {}'.format(order.id, order_link)

        EmailNotification.send_simple_email('khoa@autonomous.nyc', msg, email_content)
        SmsNotification.send_sms('+84772621770', msg)
        SlackNotification.send(slack_content)
