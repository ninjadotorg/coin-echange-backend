import logging

from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

from coin_exchange.business.crypto import TrackingManagement
from coin_exchange.business.order import OrderManagement
from coin_exchange.business.promotion import PromotionManagement
from coin_exchange.business.referral import ReferralManagement
from coin_exchange.business.user_limit import update_limit_by_level
from coin_exchange.constants import ORDER_STATUS, PAYMENT_STATUS, ORDER_TYPE
from coin_exchange.models import Order, SellingPaymentDetail
from coin_user.business import UserManagement
from coin_user.constants import VERIFICATION_STATUS
from coin_user.models import ExchangeUser
from common.constants import DIRECTION


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
    try:
        if created:
            OrderManagement.increase_limit(order.user, order.amount, order.currency, order.direction,
                                           order.fiat_local_amount, order.fiat_local_currency)
            if order.direction == DIRECTION.buy:
                if order.order_type == ORDER_TYPE.cod:
                    OrderManagement.send_new_order_notification(order)
            elif order.direction == DIRECTION.sell:
                TrackingManagement.add_tracking_address_payment(order)
                OrderManagement.send_new_order_notification(order)
        else:
            update_fields = kwargs['update_fields']
            if update_fields and 'status' in update_fields:
                if order.status in [ORDER_STATUS.expired, ORDER_STATUS.cancelled, ORDER_STATUS.rejected]:
                    OrderManagement.decrease_limit(order.user, order.amount, order.currency, order.direction,
                                                   order.fiat_local_amount, order.fiat_local_currency)
                    TrackingManagement.remove_tracking(order)
                if order.direction == DIRECTION.buy:
                    if order.status == ORDER_STATUS.fiat_transferring:
                        if order.order_type == ORDER_TYPE.bank:
                            OrderManagement.send_new_order_notification(order)
                    if order.status == ORDER_STATUS.transferring:
                        if order.tx_hash:
                            TrackingManagement.create_tracking_simple_transaction(order)
                    elif order.status == ORDER_STATUS.success:
                        UserManagement.update_first_purchase(order.user)
                        ReferralManagement.create_referral(order)
                        PromotionManagement.create_promotion(order)
                        TrackingManagement.remove_tracking(order)
                        # TODO Send notification
                elif order.direction == DIRECTION.sell:
                    if order.status == ORDER_STATUS.transferred:
                        TrackingManagement.remove_tracking(order)
                    elif order.status == ORDER_STATUS.success:
                        UserManagement.update_first_purchase(order.user)
                        ReferralManagement.create_referral(order)
                        PromotionManagement.create_promotion(order)
                        TrackingManagement.remove_tracking(order)
                        # TODO Send notification
    except Exception as ex:
        # I don't want the alter flow effect the ORDER
        logging.exception(ex)


@receiver(post_save, sender=SellingPaymentDetail)
def post_save_selling_payment_detail(sender, **kwargs):
    payment_detail = kwargs['instance']
    created = kwargs['created']
    if created:
        payment = payment_detail.payment
        order = payment.order
        test_amount = payment.amount + payment_detail.amount
        paid = False
        if test_amount == order.amount:
            payment.status = PAYMENT_STATUS.matched
            paid = True
        elif test_amount > order.amount:
            payment.status = PAYMENT_STATUS.over
            payment.overspent = test_amount - order.amount
            paid = True

        payment.amount = F('amount') + payment_detail.amount
        payment.save()

        if paid:
            order.status = ORDER_STATUS.transferred
            order.save(update_fields=['status', 'updated_at'])
