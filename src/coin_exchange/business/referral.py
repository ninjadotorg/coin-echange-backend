import logging
from datetime import timedelta
from decimal import Decimal

from django.db.models import Q

from coin_exchange.business.crypto import CryptoTransactionManagement
from coin_exchange.constants import REFERRAL_STATUS
from coin_exchange.models import Order, ReferralOrder, PromotionRule
from coin_user.business import UserWalletManagement
from coin_user.models import ExchangeUser
from common.business import get_now
from common.provider_data import ProviderData
from integration import bitstamp


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

        referrer_rule = PromotionRule.objects.filter(country=referrer.country,
                                                     currency=referrer.currency,
                                                     active=True).first()
        if referrer_rule:
            percentage = referrer_rule.referrer_percentage
            first_order = ReferralOrder.objects.filter(user=referrer, referrer=True).order_by('created_at').first()
            if first_order and referrer_rule.referrer_next_duration > 0 and \
                    first_order.created_at + timedelta(days=referrer_rule.referrer_next_duration) < get_now():
                percentage = referrer_rule.referrer_percentage_2

            bonus = (order.amount * percentage) / Decimal('100')
            if bonus:
                referrals.append(ReferralOrder(
                    order=order,
                    user=referrer,
                    amount=bonus,
                    currency=order.currency,
                    referrer=True,
                    address=UserWalletManagement.get_default_address(referrer, order.currency),
                )),

        referee_rule = PromotionRule.objects.filter(country=referee.country,
                                                    currency=referee.currency,
                                                    active=True).first()
        if referee_rule:
            percentage = referee_rule.referee_percentage
            if referee.first_purchase and referee_rule.referrer_next_duration > 0 and \
                    referee.first_purchase + timedelta(days=referee_rule.referrer_next_duration) < get_now():
                percentage = referee_rule.referee_percentage_2

            bonus = (order.amount * percentage) / Decimal('100')
            if bonus:
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

    @staticmethod
    def pay_referral():
        referral_orders = ReferralOrder.objects.filter(status=REFERRAL_STATUS.pending)
        for referral_order in referral_orders:
            try:
                tx_hash, provider_data = CryptoTransactionManagement.transfer(referral_order.address,
                                                                              referral_order.currency,
                                                                              referral_order.amount)
                referral_order.provider_data = provider_data
                referral_order.tx_hash = tx_hash
                referral_order.status = REFERRAL_STATUS.paid
                referral_order.save(update_fields=['provider_data', 'tx_hash', 'updated_at'])
            except Exception as ex:
                logging.exception(ex)

    @staticmethod
    def load_transferring_referral_to_track():
        orders = ReferralOrder.objects.filter(Q(tx_hash='') | Q(tx_hash__isnull=True),
                                              status=REFERRAL_STATUS.paid)

        list_tx = bitstamp.list_withdrawal_requests(30 * 60)
        dict_tx = {tx['id']: tx for tx in list_tx}

        for order in orders:
            try:
                data = ProviderData(None, order.provider_data).from_json()
                tx = dict_tx.get(data.get('tx_id', ''))
                if tx:
                    order.tx_hash = tx.get('transaction_id', '')
                    order.save(update_fields=['tx_hash', 'updated_at'])
            except Exception as ex:
                logging.exception(ex)
