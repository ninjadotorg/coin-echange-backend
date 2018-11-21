from django.db.models.signals import post_save
from django.dispatch import receiver

from coin_exchange.business.order import OrderManagement
from coin_exchange.business.user_limit import update_limit_by_level
from coin_exchange.constants import ORDER_STATUS
from coin_exchange.models import Order
from coin_user.constants import VERIFICATION_STATUS
from coin_user.models import ExchangeUser


@receiver(post_save, sender=ExchangeUser)
def post_save_exchange_user(sender, **kwargs):
    user = kwargs['instance']
    created = kwargs['created']
    update_fields = kwargs['update_fields']
    if not created and update_fields and 'verification_status' in update_fields:
        if user.verification_status == VERIFICATION_STATUS.approved:
            update_limit_by_level(user)


@receiver(post_save, sender=Order)
def post_save_order(sender, **kwargs):
    order = kwargs['instance']
    created = kwargs['created']
    if created:
        OrderManagement.increase_limit(order.user, order.amount, order.currency, order.direction,
                                       order.fiat_local_amount, order.fiat_local_currency)
    else:
        update_fields = kwargs['update_fields']
        if update_fields and 'status' in update_fields:
            if order.status in [ORDER_STATUS.expired, ORDER_STATUS.cancelled, ORDER_STATUS.rejected]:
                OrderManagement.decrease_limit(order.user, order.amount, order.currency, order.direction,
                                               order.fiat_local_amount, order.fiat_local_currency)
