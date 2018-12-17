from decimal import Decimal

from django.db.models import Sum, F

from coin_exchange.constants import ORDER_STATUS, CRYPTO_FUND_TYPE
from coin_exchange.models import CryptoFund, Order
from common.constants import DIRECTION


class FundManagement(object):
    @staticmethod
    def update_in_fund(currency: str):
        fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.in_fund)
        sum_amount = Order.objects.filter(direction=DIRECTION.sell,
                                          status=ORDER_STATUS.sucess,
                                          updated_at__gte=fund.updated_at).aggregate(Sum('amount'))
        fund.amount = F('amount') + sum_amount['amount__sum']
        fund.save()

    @staticmethod
    def update_out_fund(currency: str):
        fund = CryptoFund.objects.get(currency=currency, fund_type=CRYPTO_FUND_TYPE.out_fund)
        sum_amount = Order.objects.filter(direction=DIRECTION.buy,
                                          status=ORDER_STATUS.sucess,
                                          updated_at__gte=fund.updated_at).aggregate(Sum('amount'))
        fund.amount = F('amount') - sum_amount['amount__sum']
        fund.save()

    @staticmethod
    def transfer_in_fund_to_storage(amount: Decimal, currency: str):
        pass

    @staticmethod
    def transfer_storage_to_out_fund(amount: Decimal, currency: str):
        pass
