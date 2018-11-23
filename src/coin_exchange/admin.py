from django.contrib import admin

from coin_exchange.constants import ORDER_TYPE
from coin_exchange.models import Order, Review, Pool, TrackingAddress, TrackingTransaction
from common.constants import DIRECTION


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'format_amount', 'currency', 'fiat_local_amount', 'fiat_local_currency', 'status']

    def get_queryset(self, request):
        return self.model.objects.filter(direction=DIRECTION.buy, order_type=ORDER_TYPE.bank).order_by('-id')

    def has_delete_permission(self, request, obj=None):
        return False


class CODOrder(Order):
    class Meta:
        proxy = True


@admin.register(CODOrder)
class CODOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'format_amount', 'currency', 'fiat_local_amount', 'fiat_local_currency', 'status']

    def get_queryset(self, request):
        return self.model.objects.filter(direction=DIRECTION.buy, order_type=ORDER_TYPE.cod).order_by('-id')

    def has_delete_permission(self, request, obj=None):
        return False


class SellingOrder(Order):
    class Meta:
        proxy = True


@admin.register(SellingOrder)
class SellingOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'format_amount', 'currency', 'fiat_local_amount', 'fiat_local_currency', 'status']

    def get_queryset(self, request):
        return self.model.objects.filter(direction=DIRECTION.sell).order_by('-id')

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'country', 'direction', 'review']

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Pool)
class PoolAdmin(admin.ModelAdmin):
    list_display = ['direction', 'currency', 'limit', 'usage']

    def get_queryset(self, request):
        return self.model.objects.all().order_by('-id')

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TrackingAddress)
class TrackingAddressAdmin(admin.ModelAdmin):
    list_display = ['address', 'currency', 'status', 'order']


@admin.register(TrackingTransaction)
class TrackingTransactionAdmin(admin.ModelAdmin):
    list_display = ['tx_hash', 'currency', 'order', 'direction']
