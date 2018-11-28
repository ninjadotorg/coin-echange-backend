from coin_exchange.constants import REFERRER_BONUS, REFEREE_BONUS
from coin_exchange.models import Order, ReferralOrder
from coin_system.business import markup_fee
from coin_user.models import ExchangeUser


class ReferralManagement(object):
    @staticmethod
    def create_referral(order: Order):
        try:
            referrer = order.user.referral
        except ExchangeUser.DoesNotExist:
            return

        _, referrer_bonus = markup_fee(order.amount, REFERRER_BONUS)
        _, referee_bonus = markup_fee(order.amount, REFEREE_BONUS)

        ReferralOrder.objects.bulk_create(
            # Referee
            ReferralOrder(order=order,
                          user=order.user,
                          amount=referee_bonus,
                          currency=order.currency,
                          referrer=False,
                          address='',
                          ),
            ReferralOrder(order=order,
                          user=referrer,
                          amount=referrer_bonus,
                          currency=order.currency,
                          referrer=True,
                          address='',
                          ),
        )
