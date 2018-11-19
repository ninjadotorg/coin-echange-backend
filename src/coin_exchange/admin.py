from django.contrib import admin

from coin_exchange.constants import ORDER_TYPE
from coin_exchange.models import Order, Review, Pool
from common.constants import DIRECTION


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'currency', 'fiat_local_amount', 'fiat_local_currency', 'status']

    def get_queryset(self, request):
        return self.model.objects.filter(direction=DIRECTION.buy, order_type=ORDER_TYPE.bank)


class CODOrder(Order):
    class Meta:
        proxy = True


@admin.register(CODOrder)
class CODOrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'currency', 'fiat_local_amount', 'fiat_local_currency', 'status']

    def get_queryset(self, request):
        return self.model.objects.filter(direction=DIRECTION.buy, order_type=ORDER_TYPE.cod)


class SellingOrder(Order):
    class Meta:
        proxy = True


@admin.register(SellingOrder)
class SellingOrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'currency', 'fiat_local_amount', 'fiat_local_currency', 'status']

    def get_queryset(self, request):
        return self.model.objects.filter(direction=DIRECTION.sell)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'country', 'direction', 'review']


@admin.register(Pool)
class PoolAdmin(admin.ModelAdmin):
    list_display = ['direction', 'currency', 'limit', 'usage']
