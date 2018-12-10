from django.db.models import F

from coin_exchange.constants import REFERRAL_STATUS, PROMOTION
from coin_exchange.models import Order, PromotionRule, PromotionUser, PromotionOrder
from common.business import RateManagement


class PromotionManagement(object):
    @staticmethod
    def create_promotion(order: Order):
        referrer = order.user.referral
        user = order.user

        referrer_promotion = PromotionUser.objects.filter(user=referrer).first()
        currency = referrer.currency
        if referrer_promotion:
            currency = referrer_promotion.currency

        # Referral
        referrer_rule = PromotionRule.objects.filter(country=referrer.country,
                                                     currency=currency,
                                                     active=True).first()
        if referrer_rule:
            if not referrer_promotion:
                referrer_promotion = PromotionUser.objects.create(
                    user=user,
                    currency=currency,
                    referral_count=0,
                )
            else:
                # Don't need do anymore if violating below rules
                if referrer_promotion.referral_count >= referrer_rule.first_referral_count > 0:
                    return

            first_referral_count = referrer_promotion.first_referral_count
            check_amount = RateManagement.convert_currency(order.fiat_local_amount,
                                                           order.fiat_local_currency,
                                                           referrer_promotion.currency)

            referrer_promotion.first_referral_count = F('first_referral_count') + 1
            if ((referrer_rule.first_referral_count < 0 or
                 first_referral_count + 1 <= referrer_rule.first_referral_count)
                    and check_amount >= referrer_rule.first_referral_amount
                    and order.first_purchase):
                PromotionOrder.objects.create(
                    order=order,
                    user=referrer,
                    amount=referrer_rule.first_referral_referrer_bonus,
                    currency=referrer_rule.currency,
                    status=REFERRAL_STATUS.pending,
                    referrer=True,
                    note=PROMOTION.referrer)
            if order.first_purchase:
                PromotionOrder.objects.create(
                    order=order,
                    user=user,
                    amount=RateManagement.convert_currency(referrer_rule.first_referral_referee_bonus,
                                                           referrer_rule.currency, user.currency),
                    currency=user.currency,
                    status=REFERRAL_STATUS.pending,
                    referrer=False,
                    note=PROMOTION.referee)

# First click
# user_promotion = PromotionUser.objects.filter(user=user).first()
# currency = user.currency
# if user_promotion:
#     currency = user_promotion.currency
#
# user_rule = PromotionRule.objects.filter(country=referrer.country,
#                                          currency=currency,
#                                          active=True).first()
#
# if user_rule:
#     if not user_promotion:
#         user_promotion = PromotionUser.objects.create(
#             user=user,
#             currency=currency,
#             first_click_count=0,
#             first_click_amount=0,
#             first_click_expired=get_now() + timedelta(days=user_rule.first_click_days),
#         )
#     else:
#         # Don't need do anymore if violating below rules
#         if user_promotion.first_click_count >= user_rule.first_click_count:
#             return
#         if get_now() > user_promotion.first_click_expired:
#             return
#
#     first_click_count = user_promotion.first_click_count
#     first_click_amount = user_promotion.first_click_amount
#     check_amount = RateManagement.convert_currency(order.fiat_local_amount,
#                                                    order.fiat_local_currency,
#                                                    user_promotion.currency)
#
#     user_promotion.first_click_count = F('first_click_count') + 1
#     user_promotion.first_click_amount = F('first_click_amount') + check_amount
#     user_promotion.save()
#
#     # Number of purchased, total of purchased and in expiration date
#     if (first_click_count + 1 == user_rule.first_click_count and
#             first_click_amount + check_amount >= user_rule.first_click_amount and
#             get_now() < user_promotion.first_click_expired):
#         # Qualified
#         PromotionOrder.objects.create(
#             order=order,
#             user=user,
#             amount=user_rule.first_click_bonus,
#             currency=user_rule.currency,
#             status=REFERRAL_STATUS.pending,
#             referrer=True,
#             note=PROMOTION.first_click
#         )
