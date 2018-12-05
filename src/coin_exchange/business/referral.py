from datetime import timedelta
from decimal import Decimal

from coin_exchange.models import Order, ReferralOrder, PromotionRule
from coin_user.business import UserWalletManagement
from coin_user.models import ExchangeUser
from common.business import get_now


class ReferralManagement(object):
    @staticmethod
    def create_referral(order: Order):
        try:
            referrer = order.user.referral
        except ExchangeUser.DoesNotExist:
            return

        if not referrer:
            return

        referee = order.user
        referrals = []

        referrer_rule = PromotionRule.objects.filter(country=referrer.country, currency=referrer.currency).first()
        if referrer_rule:
            percentage = referrer_rule.referrer_percentage
            first_order = ReferralOrder.objects.filter(user=referrer, referrer=True).order_by('created_at').first()
            if first_order and \
                    first_order.created_at + timedelta(days=referrer_rule.referrer_next_duration) > get_now():
                percentage = referrer_rule.referrer_percentage_2

            bonus = (order.amount * percentage) / Decimal('100')
            referrals.append(ReferralOrder(
                order=order,
                user=referrer,
                amount=bonus,
                currency=order.currency,
                referrer=True,
                address=UserWalletManagement.get_default_address(referrer, order.currency),
            )),

        referee_rule = PromotionRule.objects.filter(country=referee.country, currency=referee.currency).first()
        if referee_rule:
            percentage = referee_rule.referee_percentage
            if referee.first_purchase + timedelta(days=referee_rule.referrer_next_duration) > get_now():
                percentage = referee_rule.referee_percentage_2

            bonus = (order.amount * percentage) / Decimal('100')
            referrals.append(ReferralOrder(
                order=order,
                user=referee,
                amount=bonus,
                currency=order.currency,
                referrer=True,
                address=UserWalletManagement.get_default_address(referee, order.currency),
            )),

        if referrals:
            ReferralOrder.objects.bulk_create(referrals)
